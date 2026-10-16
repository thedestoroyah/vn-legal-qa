"""Phân đoạn văn bản luật từ data/structured/*.json: theo Khoản, theo Điều và cố định theo số từ (RQ2)."""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

CHAPTER_RE = re.compile(r"^Chương\s+([IVXLC\d]+)\b", re.IGNORECASE)
SECTION_RE = re.compile(r"^Mục\s+(\d+)\b", re.IGNORECASE)
ARTICLE_RE = re.compile(r"^Điều\s+(\d+[a-zA-Z]?)\.\s*(.*)$")
CLAUSE_RE = re.compile(r"^(\d+)\.\s+(.*)$")

STRUCTURED_DIR = Path("data/structured")
LAWS_PATH = Path("data/raw/laws.json")
OUT_PATH = Path("data/processed/chunks.jsonl")
ARTICLE_OUT_PATH = Path("data/processed/chunks_article.jsonl")
FIXED_OUT_PATH = Path("data/processed/chunks_fixed.jsonl")
_CLAUSE_SUFFIX_RE = re.compile(r"_Khoan\w+$")


def _clean(line):
    return line.replace("**", "").lstrip("#").strip()


def _base(meta):
    return {
        "law_id": meta["law_id"],
        "document": meta["document"],
        "chapter": None,
        "section": None,
        "article": None,
        "article_title": None,
        "clause": None,
        "point": None,  # điểm nằm trong content của khoản, chưa tách riêng
        "effective_date": meta["effective_date"],
        "expiry_date": meta.get("expiry_date"),  # None = còn hiệu lực
        "status": meta["status"],
    }


def _article_chunks(meta, chapter, section, number, title, preamble, clauses):
    base = {**_base(meta), "chapter": chapter, "section": section,
            "article": f"Điều {number}", "article_title": title}
    prefix = f"{meta['law_id']}_Dieu{number}"
    out = []
    # Điều bị bãi bỏ không có nội dung: dùng tiêu đề để chunk không rỗng
    pre = "\n".join(preamble) or (title if not clauses else "")
    if pre:
        out.append({**base, "chunk_id": prefix, "content": pre})
    for num, lines in clauses:
        out.append({**base, "chunk_id": f"{prefix}_Khoan{num}",
                    "clause": f"Khoản {num}", "content": "\n".join(lines)})
    return out


def chunk_law(text, meta):
    chunks = []
    chapter = section = None
    article = None  # (number, title, preamble_lines, clauses)

    def flush():
        if article:
            chunks.extend(_article_chunks(meta, chapter, section, *article))

    for raw in text.splitlines():
        line = _clean(raw)
        if not line:
            continue
        if m := CHAPTER_RE.match(line):
            flush()
            article, chapter, section = None, f"Chương {m.group(1).upper()}", None
        elif m := SECTION_RE.match(line):
            flush()
            article, section = None, f"Mục {m.group(1)}"
        elif m := ARTICLE_RE.match(line):
            flush()
            article = (m.group(1), m.group(2).strip(), [], [])
        elif article is None:
            continue  # tên luật, tiêu đề chương/mục
        elif m := CLAUSE_RE.match(line):
            article[3].append((m.group(1), [m.group(2)]))
        else:
            (article[3][-1][1] if article[3] else article[2]).append(line)
    flush()

    ids = [c["chunk_id"] for c in chunks]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise ValueError(f"chunk_id trùng: {dupes}")
    if not chunks:
        raise ValueError(f"không tìm thấy 'Điều' nào trong {meta['law_id']}")
    return chunks


def _tagged_words(text):
    """Các cặp (từ, Điều chứa từ đó). Chỉ dòng tiêu đề mới đổi Điều, tránh bắt nhầm 'theo Điều 5.' giữa câu."""
    current, out = None, []
    for raw in text.splitlines():
        line = _clean(raw)
        if m := ARTICLE_RE.match(line):
            current = f"Điều {m.group(1)}"
        elif CHAPTER_RE.match(line) or SECTION_RE.match(line):
            current = None
        out += [(w, current) for w in line.split()]
    return out


def fixed_chunk(text, meta, size=200, overlap=40):
    """Baseline cắt theo số từ, không theo cấu trúc luật (so sánh RQ2); ghi các Điều mỗi đoạn phủ qua để chấm ở cấp Điều."""
    if not 0 <= overlap < size:
        raise ValueError(f"cần 0 <= overlap < size, nhận overlap={overlap}, size={size}")
    tagged = _tagged_words(text)
    step = size - overlap
    out = []
    for n, start in enumerate(range(0, len(tagged), step)):
        window = tagged[start:start + size]
        counts = collections.Counter(a for _, a in window if a)
        out.append({**_base(meta), "chunk_id": f"{meta['law_id']}_fixed{n}",
                    "content": " ".join(w for w, _ in window),
                    "articles": list(dict.fromkeys(a for _, a in window if a)),
                    # Điều chiếm nhiều từ nhất: để chấm ở cấp Điều mỗi cửa sổ chỉ tính 1 hạng
                    "main_article": counts.most_common(1)[0][0] if counts else None})
        if start + size >= len(tagged):
            break
    return out


def _strip(text):
    return text.replace("*", "").strip()


def _article_lines(articles):
    for a in articles:
        yield f"Điều {a['number']}. {_strip(a['title'])}"
        if a["text"]:
            yield _strip(a["text"])
        for c in a["clauses"]:
            yield f"{c['number']}. {_strip(c['text'])}"
            for p in c["points"]:
                yield f"{p['number']}) {_strip(p['text'])}"


def _chapter_lines(chapters):
    for ch in chapters:
        yield f"Chương {ch['number']}"
        yield _strip(ch["title"])
        yield from _article_lines(ch["articles"])
        for sec in ch["sections"]:
            yield f"Mục {sec['number']}"
            yield _strip(sec["title"])
            yield from _article_lines(sec["articles"])


def render_text(law):
    """Dựng lại văn bản theo quy ước dòng mà chunk_law/fixed_chunk đọc; bỏ tiêu đề Phần vì không phải đơn vị trích dẫn."""
    def lines():
        yield from _article_lines(law["articles"])
        for part in law["parts"]:
            yield from _article_lines(part["articles"])
            yield from _chapter_lines(part["chapters"])
        yield from _chapter_lines(law["chapters"])
    return "\n".join(lines())


def article_key(chunk_id):
    return _CLAUSE_SUFFIX_RE.sub("", chunk_id)


def article_chunks(chunks):
    """Một chunk mỗi Điều (biến thể RQ2): dẫn nhập rồi các Khoản đánh số, theo thứ tự."""
    out = {}
    for c in chunks:
        key = article_key(c["chunk_id"])
        piece = f"{c['clause'].removeprefix('Khoản ')}. {c['content']}" if c["clause"] else c["content"]
        prev = out.get(key)
        out[key] = ({**prev, "content": f"{prev['content']}\n{piece}"} if prev
                    else {**c, "chunk_id": key, "clause": None, "content": piece})
    return list(out.values())


def build_all(structured_dir, laws):
    """(chunk Khoản, chunk Điều, chunk cố định) cho mọi file JSON có số hiệu khai báo trong laws.json."""
    by_number = {info["number"].upper(): {"law_id": law_id, **info} for law_id, info in laws.items()}
    clause, fixed = [], []
    for path in sorted(Path(structured_dir).glob("*.json")):
        law = json.loads(path.read_text(encoding="utf-8"))
        meta = by_number.get(law["law_number"].upper())
        if meta is None:
            print(f"bỏ qua {path.name}: số hiệu {law['law_number']} chưa có trong laws.json", file=sys.stderr)
            continue
        text = render_text(law)
        part = chunk_law(text, meta)
        clause = clause + part
        fixed = fixed + fixed_chunk(text, meta)
        print(f"{meta['law_id']}: {len({c['article'] for c in part})} điều, {len(part)} chunk")
    return clause, article_chunks(clause), fixed


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    laws = json.loads(LAWS_PATH.read_text(encoding="utf-8"))
    clause, article, fixed = build_all(STRUCTURED_DIR, laws)
    if not clause:
        sys.exit(f"không có văn bản nào trong {STRUCTURED_DIR}/ khớp laws.json")
    for path, rows in ((OUT_PATH, clause), (ARTICLE_OUT_PATH, article), (FIXED_OUT_PATH, fixed)):
        write_jsonl(path, rows)
        print(f"{path}: {len(rows)} chunk")


if __name__ == "__main__":
    main()
