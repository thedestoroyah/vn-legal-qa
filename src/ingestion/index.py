"""Embed chunks và nạp vào ChromaDB (kèm metadata để lọc theo hiệu lực, điều, khoản)."""
import argparse
import json
import os
from pathlib import Path

import chromadb

CHUNKS_PATH = Path("data/processed/chunks.jsonl")
DB_PATH = Path("chroma_db")
COLLECTION = "legal_chunks"
BATCH = 64
DEFAULT_MODEL = "BAAI/bge-m3"
OPEN_END = 99991231  # effective_to của văn bản còn hiệu lực


def _date_int(iso):
    return int(iso.replace("-", "")) if iso else OPEN_END


def chunk_metadata(chunk):
    """Metadata cho Chroma, thêm khoảng hiệu lực dạng số vì Chroma chỉ so sánh $lt/$gte trên số."""
    # giữ None: upsert xóa được trường cũ khi nạp lại; bỏ list rỗng: Chroma từ chối
    meta = {k: v for k, v in chunk.items() if k != "content" and v != []}
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
    return lambda texts: st.encode(texts, normalize_embeddings=True).tolist()


def build_index(chunks, embed, db_path=DB_PATH, rebuild=False):
    client = chromadb.PersistentClient(path=str(db_path))
    if rebuild and COLLECTION in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION)
    col = client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    for i in range(0, len(chunks), BATCH):
        batch = chunks[i:i + BATCH]
        col.upsert(
            ids=[c["chunk_id"] for c in batch],
            embeddings=embed([embedding_text(c) for c in batch]),
            documents=[c["content"] for c in batch],
            metadatas=[chunk_metadata(c) for c in batch],
        )
    return col


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rebuild", action="store_true", help="xóa collection cũ trước khi nạp")
    ap.add_argument("--query", help="truy vấn thử sau khi nạp")
    args = ap.parse_args()

    chunks = [json.loads(line) for line in CHUNKS_PATH.read_text(encoding="utf-8").splitlines()]
    embed = make_embedder()
    col = build_index(chunks, embed, rebuild=args.rebuild)
    print(f"đã nạp {col.count()} chunk vào {DB_PATH}/")
    if args.query:
        res = col.query(query_embeddings=embed([args.query]), n_results=5)
        for cid, dist in zip(res["ids"][0], res["distances"][0]):
            print(f"{dist:.3f}  {cid}")


if __name__ == "__main__":
    main()
