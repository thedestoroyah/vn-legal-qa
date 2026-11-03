"""Embed chunks và nạp vào ChromaDB (kèm metadata để lọc theo hiệu lực, điều, khoản)."""
import argparse
import os
import time
from pathlib import Path

import chromadb

from src.ingestion.legal_chunker import read_jsonl

PROCESSED_DIR = Path("data/processed")
DB_PATH = Path("chroma_db")
COLLECTION = "legal_chunks"
BATCH = 64
DEFAULT_MODEL = "BAAI/bge-m3"
MAX_SEQ_LEN = 2048  # BGE-M3 mặc định 8192 token: vài Điều rất dài làm CPU chậm hàng chục lần
OPEN_END = 99991231  # effective_to của văn bản còn hiệu lực
VARIANTS = {  # biến thể RQ2: (file trong data/processed, collection, gắn tiêu đề phân cấp khi embed)
    "clause_header": ("chunks.jsonl", COLLECTION, True),
    "clause_plain": ("chunks.jsonl", "legal_clause_plain", False),
    "article": ("chunks_article.jsonl", "legal_article", True),
    "fixed": ("chunks_fixed.jsonl", "legal_fixed", False),
}


def _date_int(iso):
    return int(iso.replace("-", "")) if iso else OPEN_END


def chunk_metadata(chunk):
    """Metadata cho Chroma, thêm khoảng hiệu lực dạng số vì Chroma chỉ so sánh $lt/$gte trên số."""
    # bỏ None và list rỗng: có bản Chroma từ chối; trường cũ được xóa nhờ delete trước upsert trong build_index
    meta = {k: v for k, v in chunk.items() if k != "content" and v is not None and v != []}
    meta["effective_from"] = _date_int(chunk["effective_date"])
    meta["effective_to"] = _date_int(chunk.get("expiry_date"))
    return meta


def embedding_text(chunk):
    """Gắn ngữ cảnh phân cấp vào text được embed (giảm mất ngữ cảnh khi chunk nhỏ)."""
    head = " - ".join(p for p in (chunk["document"], chunk["article"], chunk["article_title"], chunk["clause"]) if p)
    return f"{head}\n{chunk['content']}"


def make_embedder(model=None):
    """EMBED_MODEL=text-embedding-3-small dùng OpenAI; mặc định BGE-M3 chạy local."""
    model = model or os.environ.get("EMBED_MODEL", DEFAULT_MODEL)
    if model.startswith("text-embedding"):
        from openai import OpenAI
        client = OpenAI()
        return lambda texts: [d.embedding for d in client.embeddings.create(model=model, input=texts).data]
    from sentence_transformers import SentenceTransformer
    st = SentenceTransformer(model)
    st.max_seq_length = MAX_SEQ_LEN
    return lambda texts: st.encode(texts, normalize_embeddings=True).tolist()


def build_index(chunks, embed, db_path=DB_PATH, rebuild=False, collection=COLLECTION, with_header=True):
    """Nạp chunk vào một collection Chroma (cosine), tính embedding theo từng lô.

    Args:
        chunks: danh sách chunk (đọc từ file .jsonl trong data/processed).
        embed: hàm nhận list[str], trả list vector (xem make_embedder).
        db_path: thư mục lưu ChromaDB.
        rebuild: True thì xóa collection cũ trước khi nạp.
        collection: tên collection.
        with_header: True thì embed văn bản kèm tiêu đề phân cấp (biến thể clause_header),
            False thì chỉ embed nội dung.

    Returns:
        Collection Chroma đã nạp; upsert nên chạy lại không sinh bản trùng.
    """
    client = chromadb.PersistentClient(path=str(db_path))
    if rebuild and collection in [c.name for c in client.list_collections()]:
        client.delete_collection(collection)
    col = client.get_or_create_collection(collection, metadata={"hnsw:space": "cosine"})
    for i in range(0, len(chunks), BATCH):
        batch = chunks[i:i + BATCH]
        ids = [c["chunk_id"] for c in batch]
        # upsert chỉ ghi đè trường có mặt; xóa trước để trường đã bỏ (vd expiry_date) không còn sót
        col.delete(ids=ids)
        col.upsert(
            ids=ids,
            embeddings=embed([embedding_text(c) if with_header else c["content"] for c in batch]),
            documents=[c["content"] for c in batch],
            metadatas=[chunk_metadata(c) for c in batch],
        )
    return col


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", choices=VARIANTS, default="clause_header")
    ap.add_argument("--rebuild", action="store_true", help="xóa collection cũ trước khi nạp")
    ap.add_argument("--query", help="truy vấn thử sau khi nạp")
    args = ap.parse_args()

    file, collection, with_header = VARIANTS[args.variant]
    chunks = read_jsonl(PROCESSED_DIR / file)
    embed = make_embedder()
    start = time.perf_counter()
    col = build_index(chunks, embed, rebuild=args.rebuild, collection=collection, with_header=with_header)
    print(f"đã nạp {col.count()} chunk vào {DB_PATH}/{collection} trong {time.perf_counter() - start:.0f}s")
    if args.query:
        res = col.query(query_embeddings=embed([args.query]), n_results=5)
        for cid, dist in zip(res["ids"][0], res["distances"][0]):
            print(f"{dist:.3f}  {cid}")


if __name__ == "__main__":
    main()
