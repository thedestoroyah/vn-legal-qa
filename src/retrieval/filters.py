"""Lọc đoạn văn bản theo khoảng hiệu lực tại một ngày, dùng chung cho BM25 (Python) và Chroma (where)."""
from datetime import date as _date

from src.ingestion.index import OPEN_END


def check_date(value):
    """None hoặc ngày ISO đã chuẩn hóa; sai định dạng thì ValueError (ngày có thể do LLM trích ra)."""
    return None if value is None else _date.fromisoformat(value).isoformat()


def is_valid_at(chunk, date=None):
    """date=None: chỉ văn bản còn hiệu lực; có date: effective_date <= date < expiry_date."""
    if date is None:
        return chunk.get("expiry_date") is None
    date = check_date(date)
    expiry = chunk.get("expiry_date")
    return chunk["effective_date"] <= date and (expiry is None or date < expiry)


def chroma_where(date=None):
    """Điều kiện `where` của Chroma cho khoảng hiệu lực tại `date` (None: chỉ văn bản còn hiệu lực), dùng trường số effective_from/effective_to."""
    if date is None:
        return {"effective_to": {"$eq": OPEN_END}}
    d = int(check_date(date).replace("-", ""))
    return {"$and": [{"effective_from": {"$lte": d}}, {"effective_to": {"$gt": d}}]}
