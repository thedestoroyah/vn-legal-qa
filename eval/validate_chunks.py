
import json
from pathlib import Path
from collections import Counter

CHUNKS_DIR = Path("../data/chunks")
VALID_TYPES = {"article", "clause", "point"}


def main():
    files = sorted(CHUNKS_DIR.glob("*.jsonl"))

    if not files:
        raise FileNotFoundError(
            f"Không tìm thấy file JSONL trong {CHUNKS_DIR.resolve()}"
        )

    chunks = []
    errors = []

    for file_path in files:
        with file_path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue

                try:
                    chunk = json.loads(line)
                    chunk["_file"] = file_path.name
                    chunks.append(chunk)
                except json.JSONDecodeError as exc:
                    errors.append(
                        f"{file_path.name}:{line_no}: JSON lỗi: {exc}"
                    )

    ids = [c.get("chunk_id") for c in chunks]
    id_counts = Counter(x for x in ids if x)

    duplicate_ids = [
        chunk_id for chunk_id, count in id_counts.items()
        if count > 1
    ]

    id_set = set(id_counts)
    missing_id = []
    empty_text = []
    invalid_type = []
    missing_parent = []
    missing_document = []

    for chunk in chunks:
        cid = chunk.get("chunk_id", "<missing>")
        text = chunk.get("text")
        chunk_type = chunk.get("chunk_type")
        parent_id = chunk.get("parent_chunk_id")

        if not chunk.get("chunk_id"):
            missing_id.append(chunk["_file"])

        if not isinstance(text, str) or not text.strip():
            empty_text.append(cid)

        if chunk_type not in VALID_TYPES:
            invalid_type.append((cid, chunk_type))

        if not chunk.get("document_id"):
            missing_document.append(cid)

        if parent_id and parent_id not in id_set:
            missing_parent.append((cid, parent_id))

    print("===== CHUNK VALIDATION REPORT =====")
    print(f"Số file: {len(files)}")
    print(f"Tổng số chunk: {len(chunks)}")
    print(f"Số chunk ID duy nhất: {len(id_set)}")
    print(f"ID trùng: {len(duplicate_ids)}")
    print(f"Thiếu chunk_id: {len(missing_id)}")
    print(f"Text rỗng: {len(empty_text)}")
    print(f"Thiếu document_id: {len(missing_document)}")
    print(f"Chunk type không hợp lệ: {len(invalid_type)}")
    print(f"Parent không tồn tại: {len(missing_parent)}")
    print(f"Lỗi JSON: {len(errors)}")

    for label, items in [
        ("ID trùng", duplicate_ids),
        ("Thiếu chunk_id", missing_id),
        ("Text rỗng", empty_text),
        ("Thiếu document_id", missing_document),
        ("Chunk type không hợp lệ", invalid_type),
        ("Parent không tồn tại", missing_parent),
        ("Lỗi JSON", errors),
    ]:
        if items:
            print(f"\n--- {label} (tối đa 10) ---")
            for item in items[:10]:
                print(item)

    if errors or duplicate_ids or missing_id or empty_text:
        print("\nKẾT LUẬN: Cần xử lý lỗi trước khi đánh giá Retrieval.")
    else:
        print("\nKẾT LUẬN: Đã qua các kiểm tra cơ bản.")


if __name__ == "__main__":
    main()
