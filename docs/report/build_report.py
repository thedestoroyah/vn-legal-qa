"""Ghép 6 chương Markdown (docs/report/chuong*_draft.md) thành báo cáo docx theo khung TDTU.

Chạy từ thư mục gốc repo (cần lệnh `pandoc`):
    python docs/report/build_report.py            # ra docs/report/final_52300098_52300106.docx
    python docs/report/build_report.py --strict   # thoát mã 1 nếu còn cảnh báo (ảnh thiếu, ghi chú nháp)

Markdown là nguồn duy nhất: sửa nội dung trong .md rồi build lại; Word chỉ dùng để cập nhật trường
(mục lục, danh mục hình/bảng) và ký tên.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import zipfile

_FIGURE = re.compile(r"<!--\s*Hình (\d+\.\d+):\s*(\S+)[^>]*?-->")
_COMMENT = re.compile(r"<!--.*?-->\n?", re.S)
_CAPTION = re.compile(r"^\*\*(Hình|Bảng) (\d+\.\d+)\.\*\*\s*(.+)$", re.M)
_HEADING_NUMBER = re.compile(r"^(#{1,4}) (?:CHƯƠNG \d+\. |\d+(?:\.\d+)+\.? |\d+\. )", re.M)
_DRAFT_MARK = re.compile(r"\[CẦN KIỂM TRA\]|\[CHỜ(?! HÌNH)|TODO")


MAX_WIDTH_CM = 15.0    # bề ngang vùng chữ của khung
MAX_HEIGHT_CM = 20.0   # chừa chỗ cho chú thích trên cùng trang
MIN_DPI = 150          # ảnh chụp màn hình độ phân giải thấp không bị phóng to quá mức này


def figure_md(rel: str, root: Path) -> str:
    """Cú pháp ảnh pandoc cho file `rel` (đường dẫn tính từ `root`), kèm chiều rộng.

    Rộng tối đa 15 cm, nhưng không vượt mức giữ ≥ 150 dpi (ảnh chụp điện thoại) và không cao quá 20 cm
    (sơ đồ dọc); làm tròn xuống 0,1 cm. File không phải PNG dùng 15 cm.
    """
    head = (root / rel).read_bytes()[:24]
    width = MAX_WIDTH_CM
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", head[16:24])
        width = min(MAX_WIDTH_CM, w / MIN_DPI * 2.54, MAX_HEIGHT_CM * w / h)
    return f"![]({rel}){{width={math.floor(width * 10) / 10:g}cm}}"


def _drop_preamble_quotes(md: str) -> str:
    # Ghi chú bản nháp nằm ở các dòng ">" giữa tiêu đề chương và tiêu đề "## " đầu tiên
    head, sep, rest = md.partition("\n## ")
    head = "\n".join(line for line in head.split("\n") if not line.startswith(">"))
    return head + sep + rest


def preprocess(md: str, root: Path) -> tuple[str, list[str]]:
    """Chuẩn hóa một chương Markdown cho pandoc.

    Bỏ ghi chú bản nháp đầu chương và comment nguồn; đổi comment hình thành ảnh (hoặc ô chờ nếu thiếu
    file); đổi dòng `**Hình X.Y.** …`/`**Bảng X.Y.** …` thành khối style Caption; bỏ số tiêu đề gõ tay
    (khung tự đánh số).

    Args:
        md: nội dung một file chuong*_draft.md.
        root: thư mục gốc để tìm ảnh (đường dẫn trong comment hình tính từ đây).

    Returns:
        (Markdown đã chuẩn hóa, danh sách cảnh báo như ảnh thiếu).
    """
    warnings: list[str] = []

    def figure(m: re.Match) -> str:
        num, rel = m.group(1), m.group(2)
        if (root / rel).is_file():
            return figure_md(rel, root) + "\n"
        warnings.append(f"thiếu ảnh Hình {num}: {rel}")
        return f"[CHỜ HÌNH {num}: {rel}]\n"

    md = _drop_preamble_quotes(md)
    md = _FIGURE.sub(figure, md)
    md = _COMMENT.sub("", md)
    md = _CAPTION.sub(lambda m: f'::: {{custom-style="Caption"}}\n{m.group(1)} {m.group(2)}. {m.group(3)}\n:::', md)
    md = _HEADING_NUMBER.sub(r"\1 ", md)
    return md, warnings


def draft_marks(md: str) -> list[str]:
    """Các dòng còn ghi chú nháp ([CẦN KIỂM TRA], [CHỜ …], TODO); ô chờ hình thiếu không tính."""
    return [line for line in md.split("\n") if _DRAFT_MARK.search(line)]


# ---------------------------------------------------------------- pandoc và hậu xử lý thân bài

@dataclass
class Part:
    """Một đoạn docx do pandoc sinh: thân bài và những gì thân bài tham chiếu."""

    body: str                                       # XML giữa <w:body> và <w:sectPr> cuối
    rels: list[tuple[str, str, str, str | None]]    # (id, type, target, targetMode) mà body dùng, theo thứ tự xuất hiện
    media: dict[str, bytes]                         # target ("media/x.png") -> nội dung
    numbering: str                                  # word/numbering.xml của pandoc
    styles: str                                     # word/styles.xml của pandoc
    namespaces: dict[str, str]                      # tiền tố -> URI khai báo ở thẻ gốc của pandoc (body dùng)


_BOOKMARK = re.compile(r"<w:bookmark(?:Start|End) [^>]*/>")
_RELATIONSHIP = re.compile(r"<Relationship [^>]*/>")
_PARAGRAPH = re.compile(r"<w:p>(?:(?!</w:p>).)*</w:p>", re.S)
_TABLE = re.compile(r"<w:tbl>.*?</w:tbl>", re.S)
_CAPTION_TEXT = re.compile(r"^(Hình|Bảng) (\d+)\.(\d+)\. (.*)$", re.S)


def _attrs(tag: str) -> dict[str, str]:
    return dict(re.findall(r'(\w+)="([^"]*)"', tag))


def _text(xml: str) -> str:
    return "".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", xml))


def pandoc_part(md: str, reference: Path, root: Path) -> Part:
    """Chạy pandoc (style lấy từ `reference`) trên Markdown đã tiền xử lý, trả phần thân bài cần ghép.

    Bỏ bookmark của pandoc (Word tự tạo bookmark mục lục khi cập nhật, và id bookmark có thể trùng khung).

    Raises:
        subprocess.CalledProcessError: pandoc lỗi (ví dụ thiếu ảnh mà Markdown vẫn trỏ tới).
    """
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "part.docx"
        subprocess.run(["pandoc", "-f", "markdown", "-t", "docx", f"--reference-doc={reference}",
                        f"--resource-path={root}", "-o", str(out)],
                       input=md, text=True, check=True, cwd=root)
        with zipfile.ZipFile(out) as z:
            doc = z.read("word/document.xml").decode("utf-8")
            rels_xml = z.read("word/_rels/document.xml.rels").decode("utf-8")
            numbering = z.read("word/numbering.xml").decode("utf-8") if "word/numbering.xml" in z.namelist() else ""
            numbering = re.sub(r"\s+/>", "/>", numbering)
            styles = z.read("word/styles.xml").decode("utf-8")
            namespaces = dict(re.findall(r'xmlns:(\w+)="([^"]+)"', doc[:doc.index(">", doc.index("<w:document")) + 1]))
            body = doc[doc.index("<w:body>") + len("<w:body>"):doc.rindex("<w:sectPr")]
            body = _BOOKMARK.sub("", re.sub(r"\s+/>", "/>", body))
            by_id = {a["Id"]: a for a in map(_attrs, _RELATIONSHIP.findall(rels_xml))}
            used = dict.fromkeys(re.findall(r'r:(?:embed|id|link)="([^"]+)"', body))
            rels = [(i, by_id[i]["Type"], by_id[i]["Target"], by_id[i].get("TargetMode")) for i in used]
            media = {t: z.read("word/" + t) for _, _, t, mode in rels if mode is None and t.startswith("media/")}
    return Part(body, rels, media, numbering, styles, namespaces)


def _run(text: str) -> str:
    return f'<w:r><w:t xml:space="preserve">{text}</w:t></w:r>'


def _field(instr: str, cached: str) -> str:
    return f'<w:fldSimple w:instr="{instr}"><w:r><w:rPr><w:noProof/></w:rPr><w:t>{cached}</w:t></w:r></w:fldSimple>'


def _caption(p: str) -> str:
    # Theo Template_VN.dotx: "Hình {STYLEREF 1 \s}.{SEQ Hình \s 1}: nội dung" để danh mục hình/bảng bắt được
    m = _CAPTION_TEXT.match(_text(p))
    if not m:
        return p
    kind, chapter, num, rest = m.groups()
    keep = "<w:keepNext/>" if kind == "Bảng" else ""      # chú thích bảng nằm trên, dính với bảng
    return (f'<w:p><w:pPr><w:pStyle w:val="Caption"/>{keep}</w:pPr>{_run(kind + " ")}'
            f'{_field(" STYLEREF 1 \\s ", chapter)}{_run(".")}{_field(f" SEQ {kind} \\* ARABIC \\s 1 ", num)}'
            f'{_run(": " + rest)}</w:p>')


def _paragraph(m: re.Match) -> str:
    p = m.group(0)
    if '<w:pStyle w:val="Caption"/>' in p:
        return _caption(p)
    if "<w:drawing>" in p:                                 # ảnh căn giữa, dính với chú thích bên dưới
        return re.sub(r'<w:pStyle w:val="[^"]*"/>', '<w:pStyle w:val="Caption"/><w:keepNext/>', p, count=1)
    return p


def postprocess_body(body: str) -> str:
    """Đổi style của pandoc sang style khung TDTU và gắn trường SEQ cho chú thích.

    FirstParagraph/BodyText/Compact → Nidungvnbn (ô bảng → Normal để khỏi thụt dòng đầu); bảng → TableGrid,
    rộng hết trang; đoạn ảnh → Caption (căn giữa); chú thích "Hình X.Y. …" → "Hình {STYLEREF}.{SEQ}: …";
    tiêu đề chương (Heading1) sang trang mới.
    """
    body = _PARAGRAPH.sub(_paragraph, body)
    body = _TABLE.sub(lambda m: m.group(0).replace('<w:pStyle w:val="Compact"/>', '<w:pStyle w:val="Normal"/>'), body)
    for old in ("FirstParagraph", "BodyText", "Compact"):
        body = body.replace(f'<w:pStyle w:val="{old}"/>', '<w:pStyle w:val="Nidungvnbn"/>')
    body = re.sub(r"<w:tblW [^>]*/>", '<w:tblW w:type="pct" w:w="5000"/>', body)          # bảng rộng hết trang
    body = body.replace('<w:pStyle w:val="Heading1"/>', '<w:pStyle w:val="Heading1"/><w:pageBreakBefore/>')
    return body.replace('<w:tblStyle w:val="Table"/>', '<w:tblStyle w:val="TableGrid"/>')


# ---------------------------------------------------------------- ghép vào khung

REPORT_DIR = Path(__file__).resolve().parent
KHUNG = REPORT_DIR / "khung_TDTU.docx"
OUT = REPORT_DIR / "final_52300098_52300106.docx"
NUM_OFFSET = 1000          # id numbering của pandoc cộng thêm để không trùng numbering của khung
DOCPR_START = 100000       # id ảnh (wp:docPr, pic:cNvPr) đánh lại từ đây, khung chỉ dùng id nhỏ hoặc ngẫu nhiên lớn
# APA 7 theo Template_VN.dotx: thụt treo 0,5"; cỡ chữ và giãn dòng như thân bài (khung đang để kiểu IEEE "[1]")
BIBLIOGRAPHY_STYLE = ('<w:style w:type="paragraph" w:styleId="Bibliography"><w:name w:val="Bibliography"/>'
                      '<w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="37"/><w:unhideWhenUsed/>'
                      '<w:pPr><w:spacing w:before="0" w:after="120" w:line="360" w:lineRule="auto"/>'
                      '<w:ind w:left="720" w:hanging="720"/></w:pPr><w:rPr><w:sz w:val="26"/><w:szCs w:val="26"/></w:rPr></w:style>')
# Style pandoc dùng nhưng khung không có (pandoc chỉ lấy style từ khung): chữ code và khối code
FALLBACK_STYLES = {
    "VerbatimChar": ('<w:style w:type="character" w:customStyle="1" w:styleId="VerbatimChar">'
                     '<w:name w:val="Verbatim Char"/><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>'
                     '<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:style>'),
    "SourceCode": ('<w:style w:type="paragraph" w:customStyle="1" w:styleId="SourceCode">'
                   '<w:name w:val="Source Code"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="0" w:after="0"/>'
                   '<w:ind w:left="567"/></w:pPr><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>'
                   '<w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr></w:style>'),
}


def _merge_numbering(base: str, part: Part, body: str) -> tuple[str, str]:
    """Chép numbering mà body dùng (id cộng NUM_OFFSET) vào numbering của khung; trả (numbering, body)."""
    used = set(re.findall(r'<w:numId w:val="(\d+)"/>', body))
    if not used:
        return base, body
    nums = {m.group(1): m.group(0) for m in re.finditer(r'<w:num w:numId="(\d+)"[^>]*>.*?</w:num>', part.numbering, re.S)}
    abstracts = {m.group(1): m.group(0) for m in
                 re.finditer(r'<w:abstractNum [^>]*w:abstractNumId="(\d+)"[^>]*>.*?</w:abstractNum>', part.numbering, re.S)}
    new_nums, new_abstracts = [], []
    for nid in sorted(used, key=int):
        num = nums[nid]
        aid = re.search(r'<w:abstractNumId w:val="(\d+)"/>', num).group(1)
        new_nums.append(num.replace(f'w:numId="{nid}"', f'w:numId="{int(nid) + NUM_OFFSET}"', 1)
                        .replace(f'<w:abstractNumId w:val="{aid}"/>', f'<w:abstractNumId w:val="{int(aid) + NUM_OFFSET}"/>'))
        abstract = abstracts[aid].replace(f'w:abstractNumId="{aid}"', f'w:abstractNumId="{int(aid) + NUM_OFFSET}"', 1)
        if abstract not in new_abstracts:
            new_abstracts.append(abstract)
    body = re.sub(r'<w:numId w:val="(\d+)"/>', lambda m: f'<w:numId w:val="{int(m.group(1)) + NUM_OFFSET}"/>', body)
    # Thứ tự bắt buộc trong numbering.xml: mọi abstractNum đứng trước mọi num
    first_num = base.index("<w:num ")
    base = base[:first_num] + "".join(new_abstracts) + base[first_num:]
    tail = base.find("<w:numIdMacAtCleanup")
    tail = base.index("</w:numbering>") if tail < 0 else tail
    return base[:tail] + "".join(new_nums) + base[tail:], body


def merge_part(files: dict[str, bytes], part: Part, tag: str) -> str:
    """Đưa quan hệ, ảnh, numbering, style mà `part.body` cần vào `files` (zip khung, sửa tại chỗ).

    Args:
        files: tên mục zip -> nội dung, của docx khung (bị sửa: rels, media, numbering, styles).
        part: phần do pandoc_part sinh, body đã qua postprocess_body.
        tag: tiền tố để id quan hệ ("rId{tag}{n}") và tên ảnh ("media/{tag}_…") không trùng khung.

    Returns:
        body đã đổi id quan hệ, id numbering.
    """
    body = part.body
    rels = files["word/_rels/document.xml.rels"].decode("utf-8")
    new_rels = []
    for n, (rid, rtype, target, mode) in enumerate(part.rels, start=1):
        new_id = f"rId{tag}{n}"
        if mode is None and target.startswith("media/"):
            new_target = f"media/{tag}_{target.split('/', 1)[1]}"
            files["word/" + new_target] = part.media[target]
        else:
            new_target = target
        mode_attr = f' TargetMode="{mode}"' if mode else ""
        new_rels.append(f'<Relationship Id="{new_id}" Type="{rtype}" Target="{new_target}"{mode_attr}/>')
        body = re.sub(rf'(r:(?:embed|id|link)=")({re.escape(rid)})(")', rf"\g<1>{new_id}\g<3>", body)
    files["word/_rels/document.xml.rels"] = rels.replace("</Relationships>", "".join(new_rels) + "</Relationships>").encode("utf-8")
    numbering, body = _merge_numbering(files["word/numbering.xml"].decode("utf-8"), part, body)
    files["word/numbering.xml"] = numbering.encode("utf-8")
    styles = files["word/styles.xml"].decode("utf-8")
    for sid, definition in FALLBACK_STYLES.items():
        if f'w:styleId="{sid}"' not in styles and f'w:val="{sid}"' in body:
            styles = styles.replace("</w:styles>", definition + "</w:styles>")
    files["word/styles.xml"] = styles.encode("utf-8")
    return body


def _heading_span(document: str, text: str) -> tuple[int, int]:
    """(đầu, cuối) của đoạn Heading1 có chữ `text` (bỏ dòng mục lục vì không mang style Heading1)."""
    for m in re.finditer(r'<w:pStyle w:val="Heading1"/>', document):
        start = max(document.rfind("<w:p ", 0, m.start()), document.rfind("<w:p>", 0, m.start()))
        end = document.index("</w:p>", m.start()) + len("</w:p>")
        if _text(document[start:end]).strip() == text:
            return start, end
    raise ValueError(f"không thấy tiêu đề Heading1 '{text}' trong khung")


def splice(document: str, start_heading: str, end_heading: str, new_xml: str) -> str:
    """Thay từ đoạn Heading1 `start_heading` tới ngay trước đoạn Heading1 `end_heading` bằng `new_xml`.

    Raises:
        ValueError: không thấy một trong hai tiêu đề.
    """
    start = _heading_span(document, start_heading)[0]
    end = _heading_span(document, end_heading)[0]
    return document[:start] + new_xml + document[end:]


def _renumber_drawings(document: str) -> str:
    # Word báo hỏng file khi hai ảnh trùng id: đánh lại id mọi wp:docPr, pic:cNvPr theo thứ tự xuất hiện
    counter = iter(range(DOCPR_START, DOCPR_START + 100000))
    return re.sub(r'(<(?:wp:docPr|pic:cNvPr)\b[^>]*?\bid=")\d+(")',      # pandoc ghi id sau descr, title
                  lambda m: f"{m.group(1)}{next(counter)}{m.group(2)}", document)


def _declare_namespaces(document: str, namespaces: dict[str, str]) -> str:
    """Thêm vào thẻ gốc <w:document> các tiền tố mà phần ghép dùng nhưng khung chưa khai báo."""
    root_end = document.index(">", document.index("<w:document"))
    root = document[:root_end]
    missing = "".join(f' xmlns:{p}="{u}"' for p, u in namespaces.items() if f"xmlns:{p}=" not in root)
    return root + missing + document[root_end:]


# ---------------------------------------------------------------- phần đầu và tài liệu tham khảo

# Nguyên văn mục 1 đề cương (tiếng Anh), in hoa như khung
EN_TITLE = ("DEVELOPING A VIETNAMESE LEGAL QUESTION ANSWERING SYSTEM BASED ON AGENTIC-RAG WITH "
            "TEMPORALLY-AWARE LEGAL RETRIEVAL AND CITATION VERIFICATION")
_INNER_PARAGRAPH = re.compile(r"<w:p(?: [^>]*)?>(?:(?!<w:p[ >]).)*?</w:p>", re.S)
_NAME = r"[A-ZĐ][\w-]+(?: [A-Z][\w-]+)?"
_CITE_ETAL = re.compile(rf"({_NAME}) và cộng sự,? \(?(\d{{4}})\)?")
_CITE_TWO = re.compile(rf"([A-ZĐ][\w-]+) (?:và|&) {_NAME},? \(?(\d{{4}})\)?")
_CITE_ONE = re.compile(rf"\(({_NAME}), (\d{{4}})\)|({_NAME}) \((\d{{4}})\)")


def set_paragraph_text(p: str, text: str) -> str:
    """Thay toàn bộ chữ của đoạn `p` bằng `text` (đã escape XML); giữ thẻ mở, pPr và rPr của run đầu."""
    open_tag = p[:p.index(">") + 1]
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", p, re.S)
    rpr = re.search(r"<w:r(?: [^>]*)?>\s*(<w:rPr>.*?</w:rPr>)", p, re.S)
    return (f"{open_tag}{ppr.group(0) if ppr else ''}<w:r>{rpr.group(1) if rpr else ''}"
            f'<w:t xml:space="preserve">{text}</w:t></w:r></w:p>')


def citation_gaps(body_md: str, refs_md: str) -> tuple[list[str], list[str]]:
    """So trích dẫn tác giả–năm trong thân bài với danh mục tài liệu (khớp theo họ tác giả đầu và năm).

    Dạng trích được nhận: "X và cộng sự (2024)", "(X và cộng sự, 2024)", "X và Y (2009)", "X & Y (2009)", "(X, 2021)", "X (2021)".

    Returns:
        (tài liệu trong danh mục không được trích, trích dẫn không có trong danh mục), mỗi mục dạng "Họ (năm)".
    """
    refs = []
    for line in refs_md.replace("*", "").splitlines():
        m = re.match(r"(.+?)(?:, |\. \()", line)
        year = re.search(r"\((\d{4})\)", line)
        if m and year:
            refs.append((m.group(1), year.group(1)))
    cited, rest = set(), body_md
    for pattern in (_CITE_ETAL, _CITE_TWO):          # bắt dạng nhiều tác giả trước để "Zaragoza (2009)" không bị đếm lẻ
        cited |= {(m.group(1), m.group(2)) for m in pattern.finditer(rest)}
        rest = pattern.sub(" ", rest)
    for m in _CITE_ONE.finditer(rest):
        cited.add((m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4)))
    uncited = [f"{a} ({y})" for a, y in refs if (a, y) not in cited]
    missing = sorted(f"{a} ({y})" for a, y in cited if (a, y) not in set(refs))
    return uncited, missing


def _find_paragraph(document: str, phrase: str, start: int = 0) -> tuple[int, int]:
    for m in _INNER_PARAGRAPH.finditer(document, start):
        if phrase in _text(m.group(0)):
            return m.start(), m.end()
    raise ValueError(f"không thấy đoạn chứa '{phrase}' trong khung")


def _sections(md: str) -> dict[str, str]:
    """Tách phan_dau.md theo tiêu đề '## ' -> nội dung."""
    return {m.group(1).strip(): m.group(2) for m in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", md, re.M | re.S)}


def fill_front_matter(document: str, files: dict[str, bytes], khung: Path, root: Path) -> str:
    """Điền phần đầu của khung: tiêu đề tiếng Anh, Tóm tắt, Abstract, bảng viết tắt, sửa lời cảm ơn và cam đoan.

    Nội dung lấy từ docs/report/phan_dau.md (mục "Tóm tắt", "Abstract", "Viết tắt").

    Raises:
        ValueError: khung thiếu đoạn mẫu cần thay; KeyError: phan_dau.md thiếu mục.
    """
    sections = _sections((root / "docs" / "report" / "phan_dau.md").read_text(encoding="utf-8"))

    def converted(name: str, tag: str) -> str:
        part = pandoc_part(sections[name], khung, root)
        part.body = postprocess_body(part.body)
        return merge_part(files, part, tag)

    s, e = _find_paragraph(document, "DEVELOPMENT OF A VIETNAMESE")
    document = document[:s] + set_paragraph_text(document[s:e], EN_TITLE) + document[e:]
    for name, tag in (("Tóm tắt", "S"), ("Abstract", "A")):       # hai ô mẫu theo thứ tự: Tóm tắt rồi Abstract
        s, e = _find_paragraph(document, "(Time New Romans")
        document = document[:s] + converted(name, tag) + document[e:]
    head_end = _heading_span(document, "DANH MỤC CÁC CHỮ VIẾT TẮT")[1]
    s = document.index("<w:tbl>", head_end)
    e = document.index("</w:tbl>", s) + len("</w:tbl>")
    document = document[:s] + converted("Viết tắt", "V") + document[e:]

    s, e = _find_paragraph(document, "đã tận tình đã tận tình")
    thanks = _text(document[s:e]).replace("đã tận tình đã tận tình", "đã tận tình").replace(
        "hướng dẫn em hoàn thành", "hướng dẫn chúng em hoàn thành")
    document = document[:s] + set_paragraph_text(document[s:e], thanks) + document[e:]
    # Cam đoan của nhóm hai người: "tôi" -> "chúng tôi", sửa trong từng run để giữ câu in đậm của mẫu
    s = _find_paragraph(document, "Tôi xin cam đoan")[0]
    e = _find_paragraph(document, "do tôi gây ra", s)[1]
    pledge = re.sub(r"(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)", lambda m: m.group(1) + re.sub(
        r"\b([Tt])ôi\b", lambda w: ("Chúng" if w.group(1) == "T" else "chúng") + " tôi", m.group(2)) + m.group(3),
        document[s:e])
    return document[:s] + pledge + document[e:]


TOC_PROMPT = ("Chưa cập nhật: mở bằng Word hoặc OnlyOffice, chọn toàn bộ (Ctrl+A) rồi nhấn F9 "
              "để cập nhật mục lục và danh mục.")
_FLDCHAR = re.compile(r'<w:fldChar\b[^>]*?w:fldCharType="(begin|separate|end)"[^>]*/>')


def clear_toc_results(document: str) -> str:
    """Thay phần kết quả lưu sẵn của các trường TOC (mục lục, danh mục hình, bảng) bằng dòng nhắc cập nhật.

    Kết quả lưu sẵn là mục lục của khung cũ (5 chương); nếu quên cập nhật trường thì dòng nhắc lộ ra
    thay vì một mục lục sai. Giữ nguyên lệnh trường để Word/OnlyOffice cập nhật được.
    """
    out, pos = [], 0
    for m in re.finditer(r"<w:instrText[^>]*> ?TOC ", document):
        sep = _FLDCHAR.search(document, m.end())
        sep_run_end = document.index("</w:r>", sep.end()) + len("</w:r>")
        depth, end = 0, None
        for f in _FLDCHAR.finditer(document, sep.end()):      # bỏ qua các trường PAGEREF lồng bên trong
            if f.group(1) == "begin":
                depth += 1
            elif f.group(1) == "end":
                if depth == 0:
                    end = f
                    break
                depth -= 1
        end_run_start = max(document.rfind("<w:r>", 0, end.start()), document.rfind("<w:r ", 0, end.start()))
        out.append(document[pos:sep_run_end] + _run(TOC_PROMPT))
        pos = end_run_start
    out.append(document[pos:])
    return "".join(out)


def chapters_md(root: Path) -> tuple[str, list[str]]:
    """Nối 6 chương đã tiền xử lý; trả (Markdown, cảnh báo: ảnh thiếu và ghi chú nháp còn sót)."""
    parts, warnings = [], []
    for path in sorted((root / "docs" / "report").glob("chuong*_draft.md")):
        md, warns = preprocess(path.read_text(encoding="utf-8"), root)
        parts.append(md)
        warnings += warns + [f"ghi chú nháp ({path.name}): {line[:80]}" for line in draft_marks(md)]
    return "\n\n".join(parts), warnings


def build(khung: Path, out: Path, root: Path) -> list[str]:
    """Sinh báo cáo docx từ khung và 6 chương Markdown; khung không bị sửa.

    Args:
        khung: docx khung TDTU (bìa, phần đầu, style, đánh số tiêu đề).
        out: file docx ra (ghi đè).
        root: thư mục gốc repo (chứa docs/report/chuong*_draft.md và ảnh).

    Returns:
        Danh sách cảnh báo (ảnh thiếu, ghi chú nháp, thiếu file tài liệu tham khảo).

    Raises:
        ValueError: khung không có tiêu đề cần thay; subprocess.CalledProcessError: pandoc lỗi.
    """
    with zipfile.ZipFile(khung) as z:
        names = z.namelist()
        files = {n: z.read(n) for n in names}
    md, warnings = chapters_md(root)
    part = pandoc_part(md, khung, root)
    part.body = postprocess_body(part.body)
    body = merge_part(files, part, "B")
    document = splice(files["word/document.xml"].decode("utf-8"), "TỔNG QUAN ĐỀ TÀI", "TÀI LIỆU THAM KHẢO", body)

    # Ngắt trang trước "TÀI LIỆU THAM KHẢO" của khung nằm trong đoạn vừa bị thay: gắn lại vào tiêu đề
    start, end = _heading_span(document, "TÀI LIỆU THAM KHẢO")
    if "<w:pageBreakBefore/>" not in document[start:end]:
        document = document[:start] + re.sub(r'(<w:pStyle w:val="Heading1"/>)', r"\1<w:pageBreakBefore/>",
                                             document[start:end], count=1) + document[end:]

    refs = root / "docs" / "report" / "tai_lieu_tham_khao.md"
    if refs.is_file():
        ref_part = pandoc_part(refs.read_text(encoding="utf-8"), khung, root)
        ref_part.body = postprocess_body(ref_part.body).replace('w:val="Nidungvnbn"', 'w:val="Bibliography"')
        ref_body = merge_part(files, ref_part, "R")
        styles = files["word/styles.xml"].decode("utf-8")
        files["word/styles.xml"] = re.sub(r'<w:style [^>]*w:styleId="Bibliography".*?</w:style>', BIBLIOGRAPHY_STYLE,
                                          styles, count=1, flags=re.S).encode("utf-8")
        head_end = _heading_span(document, "TÀI LIỆU THAM KHẢO")[1]
        document = document[:head_end] + ref_body + document[document.rindex("<w:sectPr"):]
    else:
        warnings.append("chưa có docs/report/tai_lieu_tham_khao.md: giữ danh mục cũ của khung")

    if (root / "docs" / "report" / "phan_dau.md").is_file():
        document = fill_front_matter(document, files, khung, root)
    else:
        warnings.append("chưa có docs/report/phan_dau.md: phần đầu giữ chữ mẫu của khung")
    document = clear_toc_results(document)
    document = _declare_namespaces(document, part.namespaces)
    files["word/document.xml"] = _renumber_drawings(document).encode("utf-8")
    settings = files["word/settings.xml"].decode("utf-8")
    if "<w:updateFields" not in settings:     # Word/OnlyOffice hỏi cập nhật mục lục, danh mục khi mở file
        files["word/settings.xml"] = settings.replace("</w:settings>", '<w:updateFields w:val="true"/></w:settings>').encode("utf-8")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name in names + [n for n in files if n not in names]:
            z.writestr(name, files[name])
    return warnings


def main() -> None:
    """CLI: build báo cáo, in cảnh báo; --strict thoát mã 1 nếu còn cảnh báo."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--strict", action="store_true", help="thoát mã 1 nếu còn cảnh báo")
    args = parser.parse_args()
    warnings = build(KHUNG, OUT, REPORT_DIR.parents[1])
    for w in warnings:
        print("CẢNH BÁO:", w)
    print(f"Đã ghi {OUT.relative_to(REPORT_DIR.parents[1])} ({len(warnings)} cảnh báo)")
    if args.strict and warnings:
        sys.exit(1)


if __name__ == "__main__":
    main()
