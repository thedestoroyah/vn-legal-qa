"""Chỉ số truy xuất: Hit@k, Recall@k, MRR@k (cấp Điều hoặc Khoản) và DRM@k."""
from src.ingestion.legal_chunker import article_key


def article_ranking(chunks):
    """Khóa Điều theo thứ tự xuất hiện, bỏ trùng; mỗi đoạn cố định chỉ tính Điều chính (nhiều từ nhất) của nó."""
    keys = []
    for c in chunks:
        if "articles" in c:
            main = c.get("main_article")
            found = [f"{c['law_id']}_Dieu{main.removeprefix('Điều ')}"] if main else []
        else:
            found = [article_key(c["chunk_id"])]
        keys = keys + [k for k in found if k not in keys]
    return keys


def hit_at(ranked, gold, k):
    return float(bool(set(ranked[:k]) & set(gold)))


def recall_at(ranked, gold, k):
    return len(set(ranked[:k]) & set(gold)) / len(set(gold))


def mrr_at(ranked, gold, k):
    gold = set(gold)
    return next((1.0 / rank for rank, key in enumerate(ranked[:k], 1) if key in gold), 0.0)


def drm_at(chunks, gold, k):
    """Tỷ lệ đoạn trong top-k thuộc văn bản không có trong căn cứ chuẩn; None nếu không có kết quả."""
    top = chunks[:k]
    if not top:
        return None
    gold_laws = {g.split("_", 1)[0] for g in gold}
    return sum(c["law_id"] not in gold_laws for c in top) / len(top)


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None
