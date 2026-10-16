"""Truy xuất căn cứ: BM25, Dense, Hybrid (RRF) và Hybrid + Cross-Encoder rerank, lọc theo khoảng hiệu lực."""
import re

import chromadb

from src.ingestion.index import DB_PATH, PROCESSED_DIR, VARIANTS, embedding_text, make_embedder
from src.ingestion.legal_chunker import article_chunks, article_key, read_jsonl
from src.retrieval.bm25 import BM25Index
from src.retrieval.dense import DenseIndex
from src.retrieval.filters import check_date

MODES = ("bm25", "dense", "hybrid", "hybrid_rerank")
RRF_K = 60
CANDIDATES = 50  # số ứng viên lấy từ mỗi nhánh BM25 / Dense trước khi hợp nhất
RERANK_TOP = 10  # số ứng viên đưa vào reranker; 20 mất 11 s/câu trên CPU 16 nhân (> 3 s) nên giảm còn 10
RERANK_MODEL = "BAAI/bge-reranker-v2-m3"


def rrf(rankings, k=RRF_K):
    """Reciprocal Rank Fusion: điểm = tổng 1/(k + hạng) qua các danh sách."""
    scores = {}
    for ranking in rankings:
        for rank, cid in enumerate(ranking, 1):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda item: -item[1])


def make_reranker(model=RERANK_MODEL):
    """Tạo hàm chấm điểm cross-encoder: nhận (query, list[str]) trả list[float]. Tải mô hình lần đầu rất chậm."""
    from sentence_transformers import CrossEncoder
    encoder = CrossEncoder(model, max_length=512)
    return lambda query, texts: [float(s) for s in encoder.predict([(query, t) for t in texts])]


class Retriever:
    """Gộp BM25, dense, RRF và rerank sau một giao diện; các thành phần truyền qua tham số để test bằng đối tượng giả."""
    def __init__(self, chunks, bm25, dense, rerank=None, text_fn=embedding_text):
        self.by_id = {c["chunk_id"]: c for c in chunks}
        self.bm25, self.dense, self.rerank, self.text_fn = bm25, dense, rerank, text_fn

    def search(self, query, k=5, date=None, mode="hybrid_rerank"):
        """Truy xuất top-k chunk theo chế độ chọn.

        Args:
            query: câu truy vấn; rỗng hoặc chỉ dấu câu thì trả [].
            k: số chunk trả về.
            date: ngày YYYY-MM-DD của tình huống; None chỉ lấy văn bản còn hiệu lực.
            mode: một trong MODES (bm25, dense, hybrid, hybrid_rerank).

        Returns:
            Danh sách chunk (dict) kèm `score`. Với hybrid_rerank, chỉ RERANK_TOP đầu được rerank,
            phần đuôi giữ thứ tự RRF nên `score` của phần đuôi chỉ có thứ tự là so sánh được.

        Raises:
            ValueError: mode hoặc date sai.
            RuntimeError: chỉ mục Chroma lệch với file chunk.
        """
        if mode not in MODES:
            raise ValueError(f"mode phải thuộc {MODES}, nhận {mode!r}")
        date = check_date(date)
        if not re.search(r"\w", query):
            return []  # rỗng hoặc chỉ dấu câu: không có gì để tìm
        if mode == "bm25":
            ranked = self.bm25.search(query, k, date)
        elif mode == "dense":
            ranked = self.dense.search(query, k, date)
        else:
            fused = rrf([[cid for cid, _ in index.search(query, CANDIDATES, date)] for index in (self.bm25, self.dense)])
            # phần đuôi chưa rerank vẫn giữ theo thứ tự RRF để độ sâu kết quả bằng các chế độ khác (so Recall@k công bằng);
            # điểm của phần đuôi là điểm RRF, chỉ có thứ tự là so sánh được
            ranked = fused[:k] if mode == "hybrid" else (self._rerank(query, fused[:RERANK_TOP]) + fused[RERANK_TOP:])[:k]
        self._check_known([cid for cid, _ in ranked])
        return [{**self.by_id[cid], "score": score} for cid, score in ranked]

    def _check_known(self, ids):
        stale = [cid for cid in ids if cid not in self.by_id]
        if stale:
            raise RuntimeError(f"chỉ mục lệch với file chunk ({stale[0]}): chạy lại "
                               "python -m src.ingestion.index --variant <biến thể> --rebuild")

    def _rerank(self, query, candidates):
        if self.rerank is None:
            raise RuntimeError("Retriever chưa có reranker cho mode hybrid_rerank")
        ids = [cid for cid, _ in candidates]
        self._check_known(ids)
        scores = self.rerank(query, [self.text_fn(self.by_id[cid]) for cid in ids]) if ids else []
        return sorted(zip(ids, scores), key=lambda item: -item[1])

    def get_article(self, law_id, number):
        """Toàn văn một Điều.

        Args:
            law_id: mã văn bản (vd BLDS2015).
            number: số Điều, dạng chuỗi hoặc số (vd 357, "50a").

        Returns:
            Chunk cấp Điều (chunk_id là khóa Điều, content gồm dẫn nhập và các Khoản); None nếu không có.
        """
        key = f"{law_id}_Dieu{number}"
        parts = [c for cid, c in self.by_id.items() if article_key(cid) == key]
        return article_chunks(parts)[0] if parts else None


def load_retriever(variant="clause_header", embed=None, rerank=None, db_path=DB_PATH):
    """Dựng Retriever trên một biến thể đã nạp bằng `python -m src.ingestion.index --variant <variant>`.

    Args:
        variant: một khóa của VARIANTS (clause_header, clause_plain, article, fixed).
        embed, rerank: hàm embedding/rerank; None thì tải mô hình thật.
        db_path: thư mục ChromaDB.

    Raises:
        RuntimeError: số chunk trong Chroma khác file chunk (cần nạp lại với --rebuild).
    """
    file, collection, with_header = VARIANTS[variant]
    chunks = read_jsonl(PROCESSED_DIR / file)
    col = chromadb.PersistentClient(path=str(db_path)).get_collection(collection)
    if col.count() != len(chunks):
        raise RuntimeError(f"chỉ mục {collection} có {col.count()} chunk, file chunk có {len(chunks)}: chạy lại "
                           f"python -m src.ingestion.index --variant {variant} --rebuild")
    text_fn = embedding_text if with_header else (lambda c: c["content"])
    return Retriever(chunks, BM25Index(chunks, text_fn), DenseIndex(col, embed or make_embedder()),
                     rerank or make_reranker(), text_fn)
