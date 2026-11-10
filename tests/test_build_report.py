"""Kiểm thử script ghép báo cáo docs/report/build_report.py (Markdown 6 chương → docx theo mẫu Dự án của khoa)."""
from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path
import re
import struct
import sys
import xml.dom.minidom
import zipfile
import zlib

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "report"
_spec = importlib.util.spec_from_file_location("build_report", REPORT / "build_report.py")
br = importlib.util.module_from_spec(_spec)
sys.modules["build_report"] = br        # @dataclass tra module qua sys.modules
_spec.loader.exec_module(br)
KHUNG = br.KHUNG


def png(w: int, h: int) -> bytes:
    """PNG xám hợp lệ kích thước w×h (chỉ cần header IHDR đúng cho việc đọc kích thước)."""
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    raw = b"".join(b"\x00" + b"\x80" * w for _ in range(h))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def test_preprocess_strips_draft_notes_numbers_and_comments(tmp_path):
    md = ("# CHƯƠNG 4. PHÂN TÍCH\n\n> **Bản nháp** — Đạt.\n> ghi chú\n\n## 4.1. Kiến trúc\n\n"
          "<!-- nguồn: eval/x.md\n   dòng hai -->\nBảng 4.1 cho thấy số liệu.\n\n**Bảng 4.1.** Văn bản trong kho.\n\n"
          "### 3.1 Truy xuất\n\n#### 1. Định tuyến\n\n## 2019 và sau đó\n")
    out, warns = br.preprocess(md, tmp_path)
    assert "Bản nháp" not in out and "nguồn:" not in out and "dòng hai" not in out
    assert out.startswith("# PHÂN TÍCH")
    assert "## Kiến trúc" in out and "### Truy xuất" in out and "## 2019 và sau đó" in out
    assert "#### Định tuyến" in out                          # số "1." gõ tay ở cấp 4 cũng bỏ (khung tự đánh số)
    assert "Bảng 4.1 cho thấy số liệu." in out          # câu thường giữ nguyên, không thành chú thích
    assert '::: {custom-style="Caption"}\nBảng 4.1. Văn bản trong kho.\n:::' in out
    assert warns == []


def test_preprocess_figure_marker_and_missing_file(tmp_path):
    (tmp_path / "a.png").write_bytes(png(1600, 900))
    md = ("## X\n\n<!-- Hình 4.1: a.png (nguồn a.drawio) -->\n**Hình 4.1.** Kiến trúc.\n\n"
          "<!-- Hình 3.1: thieu.png -->\n**Hình 3.1.** Chờ.\n")
    out, warns = br.preprocess(md, tmp_path)
    assert "![](a.png){width=" in out
    assert "[CHỜ HÌNH 3.1: thieu.png]" in out and any("thieu.png" in w for w in warns)
    assert '::: {custom-style="Caption"}\nHình 4.1. Kiến trúc.\n:::' in out


def test_draft_marks_ignores_missing_figure_placeholders():
    assert br.draft_marks("a\n[CHỜ HÌNH 3.1: x.png]\nb") == []
    assert br.draft_marks("Lewis (2020) `[CẦN KIỂM TRA]` x\n[CHỜ số liệu]\nTODO sửa") == [
        "Lewis (2020) `[CẦN KIỂM TRA]` x", "[CHỜ số liệu]", "TODO sửa"]


def test_sources_have_no_draft_marks():
    for p in sorted(REPORT.glob("chuong*_draft.md")):
        out, _ = br.preprocess(p.read_text(encoding="utf-8"), ROOT)
        assert br.draft_marks(out) == [], p.name


def test_every_figure_has_its_own_caption():
    for p in sorted(REPORT.glob("chuong*_draft.md")):
        assert not re.search(r"\*\*Hình \d+\.\d+–", p.read_text(encoding="utf-8")), p.name


def text_of(xml: str) -> str:
    return "".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", xml))


def test_caption_gets_chapter_and_seq_fields():
    p = '<w:p><w:pPr><w:pStyle w:val="Caption"/></w:pPr><w:r><w:t xml:space="preserve">Hình 5.3. Chênh lệch so với full.</w:t></w:r></w:p>'
    out = br.postprocess_body(p)
    assert 'w:instr=" STYLEREF 1 \\s "' in out and 'w:instr=" SEQ Hình \\* ARABIC \\s 1 "' in out
    assert text_of(out) == "Hình 5.3: Chênh lệch so với full."      # định dạng mẫu khoa: dấu hai chấm


def test_styles_mapped_images_centered_and_table_cells_not_indented():
    body = ('<w:p><w:pPr><w:pStyle w:val="FirstParagraph"/></w:pPr></w:p>'
            '<w:p><w:pPr><w:pStyle w:val="BodyText"/></w:pPr><w:r><w:drawing><wp:inline/></w:drawing></w:r></w:p>'
            '<w:tbl><w:tblPr><w:tblStyle w:val="Table"/></w:tblPr><w:tr><w:tc><w:p><w:pPr><w:pStyle w:val="Compact"/></w:pPr></w:p></w:tc></w:tr></w:tbl>'
            '<w:p><w:pPr><w:pStyle w:val="Compact"/><w:numPr><w:numId w:val="1001"/></w:numPr></w:pPr></w:p>')
    out = br.postprocess_body(body)
    assert out.count('<w:pStyle w:val="Nidungvnbn"/>') == 2           # đoạn thường + mục danh sách
    assert '<w:pStyle w:val="Caption"/><w:keepNext/>' in out             # ảnh căn giữa, dính với chú thích
    assert '<w:tblStyle w:val="TableGrid"/>' in out and '<w:pStyle w:val="BangNoiDung"/>' in out     # chữ bảng 11pt


def test_figure_width_keeps_resolution_and_fits_page(tmp_path):
    (tmp_path / "m.png").write_bytes(png(390, 844))       # ảnh chụp điện thoại: giữ ≥ 150 dpi
    (tmp_path / "s.png").write_bytes(png(3255, 5231))     # sơ đồ tuần tự cao: cao tối đa 20 cm, không thu về 6,5 cm
    (tmp_path / "w.png").write_bytes(png(1440, 900))
    assert "width=6.6cm" in br.figure_md("m.png", tmp_path)
    assert "width=12.4cm" in br.figure_md("s.png", tmp_path)
    assert "width=15cm" in br.figure_md("w.png", tmp_path)


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="cần pandoc")
def test_pandoc_part_converts_math_table_list_and_image(tmp_path):
    (tmp_path / "a.png").write_bytes(png(800, 400))
    md, _ = br.preprocess("# A\n\n## B\n\nCông thức $x^2$.\n\n- một\n- hai\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n"
                          "<!-- Hình 1.1: a.png -->\n**Hình 1.1.** Ảnh.\n", tmp_path)
    part = br.pandoc_part(md, KHUNG, tmp_path)
    assert "<m:oMath" in part.body and "<w:numPr>" in part.body and "<w:tbl>" in part.body
    assert "<w:sectPr" not in part.body and "w:bookmarkStart" not in part.body
    embeds = re.findall(r'r:embed="([^"]+)"', part.body)
    assert len(embeds) == 1 and [r[0] for r in part.rels] == embeds
    assert part.rels[0][2] in part.media and part.media[part.rels[0][2]][:4] == b"\x89PNG"


CHAPTERS = ["TỔNG QUAN ĐỀ TÀI", "TỔNG QUAN TÀI LIỆU", "CƠ SỞ LÝ THUYẾT", "PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG",
            "THỰC NGHIỆM VÀ ĐÁNH GIÁ", "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "TÀI LIỆU THAM KHẢO"]


def read_part(docx: Path, name: str) -> str:
    with zipfile.ZipFile(docx) as z:
        return z.read(name).decode("utf-8")


def zip_names(docx: Path) -> set[str]:
    with zipfile.ZipFile(docx) as z:
        return set(z.namelist())


def heading1_texts(xml: str) -> list[str]:
    out = []
    for m in re.finditer(r'<w:pStyle w:val="Heading1"/>', xml):
        start = max(xml.rfind("<w:p ", 0, m.start()), xml.rfind("<w:p>", 0, m.start()))
        out.append(text_of(xml[start:xml.index("</w:p>", m.start())]).strip())
    return out


def count_md_captions(kind: str) -> int:
    return sum(len(re.findall(rf"^\*\*{kind} \d+\.\d+\.\*\*", p.read_text(encoding="utf-8"), re.M))
               for p in REPORT.glob("chuong*_draft.md"))


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    if shutil.which("pandoc") is None:
        pytest.skip("cần pandoc")
    out = tmp_path_factory.mktemp("report") / "out.docx"
    br.build(KHUNG, out, ROOT)
    return out


def test_build_produces_six_chapters_in_order(built):
    doc = read_part(built, "word/document.xml")
    xml.dom.minidom.parseString(doc)                                   # XML hợp lệ
    assert [t for t in heading1_texts(doc) if t in CHAPTERS] == CHAPTERS


def test_every_relationship_resolves_and_drawing_ids_unique(built):
    doc, rels, names = read_part(built, "word/document.xml"), read_part(built, "word/_rels/document.xml.rels"), zip_names(built)
    ids = set(re.findall(r'Id="([^"]+)"', rels))
    assert set(re.findall(r'r:(?:embed|id)="([^"]+)"', doc)) <= ids
    for target in re.findall(r'Target="(media/[^"]+)"', rels):
        assert "word/" + target in names
    docpr = re.findall(r'<wp:docPr\b[^>]*?\bid="(\d+)"', doc)          # pandoc ghi id sau descr, title
    assert len(docpr) == len(set(docpr)) >= 13 and min(map(int, docpr)) >= br.DOCPR_START


def test_captions_use_plain_seq_lists_keep_numbering_styles_exist(built):
    doc, num, styles = (read_part(built, f"word/{n}.xml") for n in ("document", "numbering", "styles"))
    assert "Hình_2." not in doc and "Bảng_2." not in doc
    assert doc.count("SEQ Hình") == count_md_captions("Hình") and doc.count("SEQ Bảng") == count_md_captions("Bảng")
    for nid in set(re.findall(r'<w:numId w:val="(\d+)"/>', doc)) - {"0"}:     # 0 = không đánh số (OOXML)
        assert f'w:numId="{nid}"' in num
    defined = set(re.findall(r'w:styleId="([^"]+)"', styles))
    assert set(re.findall(r'<w:(?:pStyle|rStyle|tblStyle) w:val="([^"]+)"/>', doc)) <= defined
    settings = read_part(built, "word/settings.xml")
    assert '<w:updateFields w:val="true"/>' in settings
    assert settings.index("<w:updateFields") < settings.index("<w:compat")      # đúng thứ tự schema CT_Settings


def test_rebuild_is_stable_and_khung_untouched(tmp_path):
    if shutil.which("pandoc") is None:
        pytest.skip("cần pandoc")
    before = KHUNG.read_bytes()
    a, b = tmp_path / "a.docx", tmp_path / "b.docx"
    br.build(KHUNG, a, ROOT)
    br.build(KHUNG, b, ROOT)
    assert KHUNG.read_bytes() == before
    assert read_part(a, "word/document.xml") == read_part(b, "word/document.xml")


def test_chapters_start_on_new_page_and_tables_full_width(built):
    doc = read_part(built, "word/document.xml")
    for m in re.finditer(r'<w:pStyle w:val="Heading1"/>', doc):
        start = max(doc.rfind("<w:p ", 0, m.start()), doc.rfind("<w:p>", 0, m.start()))
        para = doc[start:doc.index("</w:p>", m.start())]
        if text_of(para).strip() in CHAPTERS:
            assert "<w:pageBreakBefore/>" in para, text_of(para)
    body = doc[doc.index("TỔNG QUAN ĐỀ TÀI</w:t>"):]
    assert '<w:tblW w:type="auto"' not in body and body.count('<w:tblW w:type="pct" w:w="5000"/>') >= 20


def test_citation_gaps_finds_uncited_and_missing():
    refs = "Gao, T., & Chen, D. (2023). *A*.\n\nNguyen Ba, T. (2024). B.\n\nRobertson, S., & Zaragoza, H. (2009). C.\n\nZalo AI. (2021). D.\n"
    body = ("Gao và cộng sự (2023) và (Nguyen Ba và cộng sự, 2024); Robertson & Zaragoza (2009) đề xuất BM25. "
            "Bộ luật Lao động 2012, ALQAC 2025, BLLĐ 2019. Foo và cộng sự (2099).")
    assert br.citation_gaps(body, refs) == (["Zalo AI (2021)"], ["Foo (2099)"])


def test_citations_and_references_match():
    body = "\n".join(p.read_text(encoding="utf-8") for p in sorted(REPORT.glob("chuong*_draft.md")))
    assert br.citation_gaps(body, (REPORT / "tai_lieu_tham_khao.md").read_text(encoding="utf-8")) == ([], [])


def test_reference_list_is_the_outline_list():
    refs = [l for l in (REPORT / "tai_lieu_tham_khao.md").read_text(encoding="utf-8").splitlines() if re.match(r"\w", l)]
    # APA 7 (9.44) "nothing precedes something": Nguyen, T.-M. đứng trước Nguyen Ba
    assert len(refs) == 15 and refs == sorted(refs, key=lambda r: (r.split(",")[0].casefold(), r.casefold()))
    assert all("*" in r for r in refs)                                   # APA 7: tên nguồn in nghiêng


def test_set_paragraph_text_keeps_paragraph_and_first_run_format():
    p = ('<w:p w14:paraId="1"><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:b/></w:rPr><w:t>A</w:t></w:r>'
         '<w:r><w:br/></w:r><w:r><w:t>B</w:t></w:r></w:p>')
    assert br.set_paragraph_text(p, "X &amp; Y") == ('<w:p w14:paraId="1"><w:pPr><w:jc w:val="center"/></w:pPr>'
                                                   '<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">X &amp; Y</w:t></w:r></w:p>')


def test_front_matter_filled(built):
    doc = read_part(built, "word/document.xml")
    text = text_of(doc)
    assert "Time New Romans" not in text
    assert ("DEVELOPING A VIETNAMESE LEGAL QUESTION ANSWERING SYSTEM BASED ON AGENTIC-RAG WITH "
            "TEMPORALLY-AWARE LEGAL RETRIEVAL AND CITATION VERIFICATION") in text
    for sample in ("HỌ VÀ TÊN SINH VIÊN", "TÊN ĐỀ TÀI", "TÊN CHUYÊN NGÀNH", "Nguyễn Văn A", "NĂM …", "20..",
                   "TITLE", "……", "PHẦN XÁC NHẬN", "Hochreiter", "Scaled Dot-Product"):   # không dùng "VLSP": Chương 2 có nhắc
        assert sample not in text, sample
    assert text.count("PHẠM HUỲNH QUỐC ĐẠT - 52300098") == 2 and text.count("HOÀNG SINH HÙNG - 52300106") == 2
    assert text.count(br.VI_TITLE) == 3 and text.count("KHOA HỌC MÁY TÍNH") == 2
    assert "PGS.TS. Lê Anh Cường" in text and text.count("NĂM 2026") == 2 and text.count("năm 2026") == 2
    assert "hướng dẫn chúng em hoàn thành" in text and "đã tận tình đã tận tình" not in text
    assert "Chúng tôi xin cam đoan" in text and "của riêng chúng tôi" in text and "do chúng tôi gây ra" in text
    assert "Reciprocal Rank Fusion" in text and "[14]" not in text   # bảng viết tắt có nội dung; danh mục IEEE cũ đã thay
    assert "Asai, A." in text and "Zalo AI. (2021)" in text


def test_bibliography_style_is_apa_hanging_indent_body_size(built):
    styles = read_part(built, "word/styles.xml")
    bib = re.search(r'<w:style [^>]*w:styleId="Bibliography".*?</w:style>', styles, re.S).group(0)
    assert '<w:ind w:left="720" w:hanging="720"/>' in bib and '<w:sz w:val="26"/>' in bib
    assert 'w:after="0" w:line="480"' in bib                         # giãn dòng đôi như Template_VN.dotx


def test_stale_toc_results_replaced_by_update_prompt(built):
    doc = read_part(built, "word/document.xml")
    text = text_of(doc)
    assert "No table of figures entries found" not in text and "LangGrahp" not in text   # chữ lưu sẵn của mục lục cũ
    assert len(re.findall(r"<w:instrText[^>]*> ?TOC ", doc)) == 3
    assert text.count(br.TOC_PROMPT) == 3


def test_abbreviations_appear_in_chapters_and_cover_common_ones():
    body = "\n".join(p.read_text(encoding="utf-8") for p in REPORT.glob("chuong*_draft.md"))
    rows = re.findall(r"^\| (\S+) \| ", (REPORT / "phan_dau.md").read_text(encoding="utf-8"), re.M)
    for abbr in rows:
        assert re.search(rf"(?<![\w-]){re.escape(abbr)}(?![A-Za-zÀ-ỹ-])", body), abbr      # cho phép "RQ1", "MRR@10"
    assert {"ALCE", "AI", "JSONL", "BGE-M3"} <= set(rows) and "BGE" not in rows


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="cần pandoc")
def test_list_right_after_paragraph_is_a_list(tmp_path):
    part = br.pandoc_part("## A\n\nCác nhóm câu hỏi:\n- *một:* x\n- *hai:* y\n", KHUNG, tmp_path)
    assert part.body.count("<w:numPr>") == 2                    # không bị nối vào đoạn văn phía trên


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="cần pandoc")
def test_markdown_footnote_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="chân trang"):
        br.pandoc_part("Câu[^1].\n\n[^1]: Ghi chú.\n", KHUNG, tmp_path)


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="cần pandoc")
def test_two_parts_with_lists_get_distinct_numbering(tmp_path):
    with zipfile.ZipFile(KHUNG) as z:
        files = {n: z.read(n) for n in z.namelist()}
    bodies = []
    for tag in ("X", "Y"):
        part = br.pandoc_part("## A\n\n- một\n- hai\n", KHUNG, tmp_path)
        part.body = br.postprocess_body(part.body)
        bodies.append(br.merge_part(files, part, tag))
    ids = [set(re.findall(r'<w:numId w:val="(\d+)"/>', b)) for b in bodies]
    assert ids[0] and ids[1] and not ids[0] & ids[1]
    num = files["word/numbering.xml"].decode("utf-8")
    nums = re.findall(r'<w:num w:numId="(\d+)"', num)
    abstracts = re.findall(r'<w:abstractNum [^>]*w:abstractNumId="(\d+)"', num)
    assert len(nums) == len(set(nums)) and len(abstracts) == len(set(abstracts))


def test_new_image_extension_gets_content_type():
    files = {"[Content_Types].xml": b'<Types><Default Extension="png" ContentType="image/png"/></Types>',
             "word/_rels/document.xml.rels": b"<Relationships></Relationships>",
             "word/numbering.xml": b"<w:numbering></w:numbering>", "word/styles.xml": b"<w:styles></w:styles>"}
    image = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
    part = br.Part('<w:p><a:blip r:embed="rId9"/></w:p>', [("rId9", image, "media/x.svg", None)],
                   {"media/x.svg": b"<svg/>"}, "", "", {})
    br.merge_part(files, part, "T")
    assert b'<Default Extension="svg" ContentType="image/svg+xml"/>' in files["[Content_Types].xml"]
    assert files["word/media/T_x.svg"] == b"<svg/>"


def test_no_unreferenced_media_left_in_package(built):
    names = zip_names(built)
    targets = set()
    for rels in (n for n in names if n.startswith("word/_rels/") and n.endswith(".rels")):
        targets |= {"word/" + t for t in re.findall(r'Target="(media/[^"]+)"', read_part(built, rels))}
    assert {n for n in names if n.startswith("word/media/")} == targets
    doc = read_part(built, "word/document.xml")
    used = set(re.findall(r'r:(?:embed|id|link)="([^"]+)"', doc))
    for tag in re.findall(r"<Relationship [^>]*/>", read_part(built, "word/_rels/document.xml.rels")):
        if tag.count("/image\"") or 'relationships/image"' in tag:
            assert re.search(r'Id="([^"]+)"', tag).group(1) in used, tag     # ảnh chương cũ của khung đã bỏ


def test_table_columns_fit_their_longest_word():
    tbl = ('<w:tbl><w:tblPr><w:tblStyle w:val="Table"/><w:tblW w:type="auto" w:w="0"/><w:tblLook w:val="0020"/></w:tblPr>'
           '<w:tblGrid><w:gridCol w:w="4252"/><w:gridCol w:w="4252"/></w:tblGrid><w:tr>'
           '<w:tc><w:tcPr/><w:p><w:r><w:t>Faithfulness</w:t></w:r></w:p></w:tc>'
           '<w:tc><w:tcPr/><w:p><w:r><w:t>x</w:t></w:r></w:p></w:tc></w:tr></w:tbl>')
    out = br.postprocess_body(tbl)
    cols = [int(w) for w in re.findall(r'<w:gridCol w:w="(\d+)"/>', out)]
    assert cols[0] > cols[1] and sum(cols) == br.TABLE_WIDTH_TWIPS
    assert '<w:tblLayout w:type="fixed"/><w:tblLook' in out
    assert [int(w) for w in re.findall(r'<w:tcW w:w="(\d+)" w:type="dxa"/>', out)] == cols


def test_table_text_style_is_11pt_single_spaced(built):
    styles = read_part(built, "word/styles.xml")
    style = re.search(r'<w:style [^>]*w:styleId="BangNoiDung".*?</w:style>', styles, re.S).group(0)
    assert '<w:sz w:val="22"/>' in style and 'w:line="240"' in style


def test_replace_paragraphs_swaps_every_exact_match_and_escapes():
    p = '<w:p><w:r><w:rPr><w:b/></w:rPr><w:t>TÊN </w:t></w:r><w:r><w:t>ĐỀ TÀI</w:t></w:r></w:p>'
    doc = p + '<w:p><w:r><w:t>TÊN ĐỀ TÀI dài hơn</w:t></w:r></w:p>' + p
    out = br.replace_paragraphs(doc, {"TÊN ĐỀ TÀI": "A & B"})
    assert out.count("A &amp; B") == 2 and "TÊN ĐỀ TÀI dài hơn" in out      # chỉ thay đoạn khớp nguyên văn
    with pytest.raises(ValueError, match="TITLE"):
        br.replace_paragraphs(doc, {"TITLE": "x"})                          # chữ mẫu không còn: dừng, nêu tên


def test_set_paragraph_text_takes_format_of_first_run_with_text():
    p = '<w:p><w:r><w:rPr><w:i/></w:rPr><w:t></w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:t>X</w:t></w:r></w:p>'
    assert "<w:b/>" in br.set_paragraph_text(p, "Y") and "<w:i/>" not in br.set_paragraph_text(p, "Y")
    p = '<w:p><w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve"> </w:t></w:r><w:r><w:rPr><w:i/></w:rPr><w:t>X</w:t></w:r></w:p>'
    assert "<w:i/>" in br.set_paragraph_text(p, "Y") and "<w:b/>" not in br.set_paragraph_text(p, "Y")   # bỏ run chỉ có dấu cách


def test_set_paragraph_text_keeps_page_break():
    p = '<w:p><w:r><w:t>NĂM …</w:t><w:br w:type="page"/></w:r></w:p>'
    assert br.set_paragraph_text(p, "NĂM 2026").endswith('<w:t xml:space="preserve">NĂM 2026</w:t></w:r><w:r><w:br w:type="page"/></w:r></w:p>')


def test_output_is_a_document_with_template_margins(built):
    types = read_part(built, "[Content_Types].xml")
    assert "document.main+xml" in types and "template.main+xml" not in types
    margins = re.findall(r"<w:pgMar [^>]*/>", read_part(built, "word/document.xml"))
    assert len(margins) == 5
    assert all('w:top="1985"' in m and 'w:right="1134"' in m and 'w:bottom="1701"' in m and 'w:left="1985"' in m
               for m in margins)


def test_cover_spacers_after_students_and_project_line_dropped():
    def para(t: str = "") -> str:
        return f"<w:p><w:r><w:t>{t}</w:t></w:r></w:p>"
    logo = "<w:p><w:r><w:drawing/></w:r></w:p>"
    cover = (para() + logo + para("HOÀNG SINH HÙNG - 52300106") + para() + para() + para(br.VI_TITLE) + para()
             + para("DỰ ÁN CÔNG NGHỆ THÔNG TIN") + para() + para() + para("KHOA HỌC MÁY TÍNH") + para())
    rest = '<w:p><w:pPr><w:sectPr/></w:pPr></w:p>' + para() + para("DỰ ÁN CÔNG NGHỆ THÔNG TIN") + para()
    out = br.drop_cover_spacers(cover + rest)
    assert out == (para() + logo + para("HOÀNG SINH HÙNG - 52300106") + para(br.VI_TITLE) + para()
                   + para("DỰ ÁN CÔNG NGHỆ THÔNG TIN") + para("KHOA HỌC MÁY TÍNH") + para() + rest)   # sau bìa: không đụng


def test_break_only_paragraph_becomes_page_break_before_next():
    brk = '<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:br w:type="page"/></w:r></w:p>'
    toc = '<w:p><w:pPr><w:pStyle w:val="Nidungvnbn"/><w:jc w:val="center"/></w:pPr><w:r><w:t>MỤC LỤC</w:t></w:r></w:p>'
    plain = '<w:p><w:r><w:t>X</w:t></w:r></w:p>'
    section = '<w:p><w:pPr><w:sectPr/></w:pPr><w:r><w:br w:type="page"/></w:r></w:p>'
    out = br.page_breaks_to_before(brk + toc + brk + plain + section + plain)
    assert out == ('<w:p><w:pPr><w:pStyle w:val="Nidungvnbn"/><w:pageBreakBefore/><w:jc w:val="center"/></w:pPr>'
                   '<w:r><w:t>MỤC LỤC</w:t></w:r></w:p>'
                   '<w:p><w:pPr><w:pageBreakBefore/></w:pPr><w:r><w:t>X</w:t></w:r></w:p>' + section + plain)
    assert br.page_breaks_to_before(brk + "<w:tbl></w:tbl>") == brk + "<w:tbl></w:tbl>"    # sau là bảng: giữ nguyên


def test_no_dotted_filler_line_left_in_front_matter(built):
    doc = read_part(built, "word/document.xml")
    filler = [p for p in re.findall(r"<w:p[ >](?:(?!<w:p[ >]).)*?</w:p>", doc, re.S)
              if "<w:tab/>" in p and 'w:leader="dot"' in p and not text_of(p).strip()]
    assert filler == []                                                   # dòng chấm mẫu dưới Tóm tắt, Abstract


def test_paragraph_ids_unique(built):
    ids = re.findall(r'w14:paraId="([^"]+)"', read_part(built, "word/document.xml"))
    assert len(ids) == len(set(ids))


def test_file_author_is_the_students(built):
    core = read_part(built, "docProps/core.xml")
    assert f"<dc:creator>{br.AUTHORS}</dc:creator>" in core and f"<cp:lastModifiedBy>{br.AUTHORS}</cp:lastModifiedBy>" in core


def test_no_template_highlight_left(built):
    assert "<w:highlight" not in read_part(built, "word/document.xml")   # mẫu tô vàng chữ cần thay (tên GVHD ở cam đoan)
