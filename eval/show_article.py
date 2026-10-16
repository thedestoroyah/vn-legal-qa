"""In toàn văn một Điều kèm chunk_id để gán căn cứ: python -m eval.show_article BLLD2019 35"""
import argparse

from src.ingestion.legal_chunker import OUT_PATH, article_key, read_jsonl


def format_article(chunks, law_id, number):
    """Chuỗi toàn văn một Điều: dòng tiêu đề rồi từng dòng `[chunk_id] nội dung`; thông báo không tìm thấy nếu thiếu. Dùng để chép mã căn cứ cho gold_citations."""
    key = f"{law_id}_Dieu{number}"
    parts = [c for c in chunks if article_key(c["chunk_id"]) == key]
    if not parts:
        return f"Không tìm thấy {law_id} Điều {number}"
    head = f"{law_id} {parts[0]['article']}. {parts[0]['article_title']}"
    return "\n".join([head] + [f"[{c['chunk_id']}] {c['content']}" for c in parts])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("law_id")
    ap.add_argument("number")
    args = ap.parse_args()
    print(format_article(read_jsonl(OUT_PATH), args.law_id, args.number))


if __name__ == "__main__":
    main()
