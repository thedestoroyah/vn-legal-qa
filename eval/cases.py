"""Schema và kiểm tra hợp lệ tập câu hỏi kiểm thử (Phụ lục A.4)."""
from datetime import date

from src.ingestion.legal_chunker import article_key

TYPES = {"situational", "temporal", "direct", "out_of_scope"}
DOMAINS = {"dan_su", "lao_dong", "doanh_nghiep", "thuong_mai", "ngoai_pham_vi"}
SOURCES = {"zalo", "synthetic", "manual"}
FIELDS = ("id", "question", "type", "domain", "event_date", "gold_citations", "reference_answer", "source",
          "checked_by")


def is_iso_date(value):
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return len(value) == 10  # fromisoformat nhận cả "20200301"; tập kiểm thử chỉ dùng dạng YYYY-MM-DD


def _case_errors(case, chunk_ids, article_keys):
    errors = [f"{field}={case[field]!r} không hợp lệ"
              for field, allowed in (("type", TYPES), ("domain", DOMAINS), ("source", SOURCES))
              if case[field] not in allowed]
    if not str(case["question"]).strip():
        errors.append("question rỗng")
    if case["event_date"] is not None and not is_iso_date(case["event_date"]):
        errors.append(f"event_date={case['event_date']!r} không phải YYYY-MM-DD")
    if case["type"] == "temporal" and case["event_date"] is None:
        errors.append("câu temporal phải có event_date")
    gold = case["gold_citations"]
    if not isinstance(gold, list):
        return errors + ["gold_citations phải là danh sách"]
    if case["type"] == "out_of_scope" and gold:
        errors.append("câu out_of_scope phải có gold_citations rỗng")
    if case["type"] != "out_of_scope" and not gold:
        errors.append("thiếu gold_citations")
    return errors + [f"căn cứ {g} không có trong kho" for g in gold if g not in chunk_ids and g not in article_keys]


def validate_cases(cases, chunk_ids):
    """Danh sách lỗi '<id>: <mô tả>'; rỗng nghĩa là hợp lệ. chunk_ids: mọi chunk_id trong chunks.jsonl."""
    chunk_ids = set(chunk_ids)
    article_keys = {article_key(c) for c in chunk_ids}
    errors, seen = [], set()
    for i, case in enumerate(cases):
        cid = case.get("id", f"#{i}")
        missing = [f for f in FIELDS if f not in case]
        if missing:
            errors.append(f"{cid}: thiếu trường {', '.join(missing)}")
            continue
        if cid in seen:
            errors.append(f"{cid}: id trùng")
        seen.add(cid)
        errors += [f"{cid}: {e}" for e in _case_errors(case, chunk_ids, article_keys)]
    return errors
