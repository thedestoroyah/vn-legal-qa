"""Chỉ số truy xuất: Hit@k, Recall@k, MRR@k (cấp Điều hoặc Khoản) và DRM@k."""
from src.ingestion.legal_chunker import article_key


def article_ranking(chunks):
    """Xếp hạng cấp Điều từ danh sách chunk: trả list khóa Điều theo thứ tự xuất hiện, bỏ trùng (đoạn cố định chỉ tính Điều chính)."""
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
    """1.0 nếu top-k của `ranked` chứa ít nhất một phần tử của `gold`, ngược lại 0.0."""
    return float(bool(set(ranked[:k]) & set(gold)))


def recall_at(ranked, gold, k):
    """Tỷ lệ phần tử `gold` xuất hiện trong top-k của `ranked` (gold không rỗng)."""
    return len(set(ranked[:k]) & set(gold)) / len(set(gold))


def mrr_at(ranked, gold, k):
    """Nghịch đảo hạng của phần tử gold đầu tiên trong top-k của `ranked`; 0.0 nếu không có."""
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
    """Trung bình, bỏ qua None; None nếu không còn giá trị nào."""
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def citation_pr(cited, gold):
    """Precision và recall trích dẫn ở cấp Điều.

    Args:
        cited: khóa Điều được trích trong câu trả lời (có thể rỗng).
        gold: khóa Điều của căn cứ chuẩn (rỗng với câu out_of_scope).

    Returns:
        (precision, recall); precision = None khi không trích gì, recall = None khi gold rỗng.
    """
    cited, gold = set(cited), set(gold)
    hit = len(cited & gold)
    return (hit / len(cited) if cited else None, hit / len(gold) if gold else None)


def refusal_correct(case, response):
    """True khi tác tử từ chối đúng câu out_of_scope, hoặc không từ chối câu trong phạm vi."""
    return response["refused"] == (case["type"] == "out_of_scope")


def version_correct(case, cited_laws):
    """RQ4: câu temporal đúng phiên bản khi có trích dẫn và mọi văn bản được trích thuộc căn cứ chuẩn; câu khác trả None.

    Args:
        case: câu kiểm thử (cần type, gold_citations).
        cited_laws: law_id của các trích dẫn trong câu trả lời.
    """
    if case["type"] != "temporal":
        return None
    gold = {g.split("_", 1)[0] for g in case["gold_citations"]}
    return bool(cited_laws) and set(cited_laws) <= gold
