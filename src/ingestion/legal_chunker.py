"""Tách văn bản luật thành chunk theo Chương > Mục > Điều > Khoản (điểm nằm trong khoản)."""
import argparse
import json
import re
import sys
from pathlib import Path

CHAPTER_RE = re.compile(r"^Chương\s+([IVXLC\d]+)\b", re.IGNORECASE)
SECTION_RE = re.compile(r"^Mục\s+(\d+)\b", re.IGNORECASE)
ARTICLE_RE = re.compile(r"^Điều\s+(\d+[a-zA-Z]?)\.\s*(.*)$")
CLAUSE_RE = re.compile(r"^(\d+)\.\s+(.*)$")

RAW_DIR = Path("data/raw")
OUT_PATH = Path("data/processed/chunks.jsonl")
FIXED_OUT_PATH = Path("data/processed/chunks_fixed.jsonl")


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
        out.append({**_base(meta), "chunk_id": f"{meta['law_id']}_fixed{n}",
                    "content": " ".join(w for w, _ in window),
                    "articles": list(dict.fromkeys(a for _, a in window if a))})
        if start + size >= len(tagged):
            break
    return out


def _write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fixed", action="store_true", help="ghi thêm chunks_fixed.jsonl (baseline RQ2)")
    args = ap.parse_args()

    laws = json.loads((RAW_DIR / "laws.json").read_text(encoding="utf-8"))
    recursive, fixed = [], []
    for law_id, info in laws.items():
        path = RAW_DIR / f"{law_id}.md"
        if not path.exists():
            print(f"bỏ qua {law_id}: thiếu {path}", file=sys.stderr)
            continue
        text, meta = path.read_text(encoding="utf-8"), {"law_id": law_id, **info}
        part = chunk_law(text, meta)
        recursive += part
        fixed += fixed_chunk(text, meta)
        print(f"{law_id}: {len({c['article'] for c in part})} điều, {len(part)} chunk")
    if not recursive:
        sys.exit("không có file luật nào trong data/raw/")
    _write_jsonl(OUT_PATH, recursive)
    if args.fixed:
        _write_jsonl(FIXED_OUT_PATH, fixed)


if __name__ == "__main__":
    main()
