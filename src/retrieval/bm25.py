"""Tìm kiếm từ khóa BM25 trên từ đã tách bằng underthesea (từ ghép nối bằng _)."""
import re

from rank_bm25 import BM25Okapi
from underthesea import word_tokenize

from src.retrieval.filters import check_date, is_valid_at

_PUNCT_RE = re.compile(r"[^\w\s]")


def tokenize(text):
    """Tách từ tiếng Việt bằng underthesea (từ ghép nối bằng `_`), chữ thường, bỏ dấu câu. Trả list[str]."""
    return _PUNCT_RE.sub(" ", word_tokenize(text, format="text").lower()).split()


class BM25Index:
    """Chỉ mục BM25 trong bộ nhớ trên danh sách chunk."""
    # shortcut: dựng lại chỉ mục mỗi lần khởi động (~10 giây cho 4 luật); lưu ra đĩa nếu kho lớn hơn nhiều
    def __init__(self, chunks, text_fn=lambda c: c["content"]):
        self.chunks = chunks
        self.bm25 = BM25Okapi([tokenize(text_fn(c)) for c in chunks])

    def search(self, query, k=50, date=None):
        """Tìm theo từ khóa BM25, chỉ giữ chunk có hiệu lực tại `date`.

        Args:
            query: câu truy vấn.
            k: số kết quả tối đa.
            date: ngày YYYY-MM-DD; None chỉ lấy văn bản còn hiệu lực.

        Returns:
            Danh sách (chunk_id, điểm) giảm dần theo điểm, bỏ chunk điểm 0; rỗng nếu truy vấn không có từ nào.
        """
        date = check_date(date)
        tokens = tokenize(query)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        valid = (i for i, c in enumerate(self.chunks) if is_valid_at(c, date) and scores[i] > 0)
        ranked = sorted(valid, key=lambda i: -scores[i])[:k]
        return [(self.chunks[i]["chunk_id"], float(scores[i])) for i in ranked]
