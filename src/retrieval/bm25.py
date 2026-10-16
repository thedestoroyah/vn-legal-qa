"""Tìm kiếm từ khóa BM25 trên từ đã tách bằng underthesea (từ ghép nối bằng _)."""
import re

from rank_bm25 import BM25Okapi
from underthesea import word_tokenize

from src.retrieval.filters import check_date, is_valid_at

_PUNCT_RE = re.compile(r"[^\w\s]")


def tokenize(text):
    return _PUNCT_RE.sub(" ", word_tokenize(text, format="text").lower()).split()


class BM25Index:
    # shortcut: dựng lại chỉ mục mỗi lần khởi động (~10 giây cho 4 luật); lưu ra đĩa nếu kho lớn hơn nhiều
    def __init__(self, chunks, text_fn=lambda c: c["content"]):
        self.chunks = chunks
        self.bm25 = BM25Okapi([tokenize(text_fn(c)) for c in chunks])

    def search(self, query, k=50, date=None):
        date = check_date(date)
        tokens = tokenize(query)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        valid = (i for i, c in enumerate(self.chunks) if is_valid_at(c, date) and scores[i] > 0)
        ranked = sorted(valid, key=lambda i: -scores[i])[:k]
        return [(self.chunks[i]["chunk_id"], float(scores[i])) for i in ranked]
