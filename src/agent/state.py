"""Trạng thái tác tử LangGraph và 5 cấu hình thí nghiệm RQ3 (spec mục 5)."""
import operator
from typing import Annotated, TypedDict

TOP_K = 5
MAX_REWRITES = 2
MAX_EVIDENCE = TOP_K * (MAX_REWRITES + 1)  # đủ chỗ cho mọi vòng viết lại, không đẩy mất đoạn đã tìm được

CONFIGS = {
    "baseline": {"use_router": False, "use_grading": False, "use_verify": False},
    "full": {"use_router": True, "use_grading": True, "use_verify": True},
    "no_router": {"use_router": False, "use_grading": True, "use_verify": True},
    "no_grading": {"use_router": True, "use_grading": False, "use_verify": True},
    "no_verify": {"use_router": True, "use_grading": True, "use_verify": False},
}

# RQ4: event = lọc theo ngày router trích ra; current = chỉ văn bản còn hiệu lực; any = không lọc
DATE_POLICIES = ("event", "current", "any")


class AgentState(TypedDict, total=False):
    """Trạng thái chạy qua các nút; mỗi nút trả về phần cập nhật, riêng `trace` được nối thêm."""

    question: str
    date_policy: str  # một phần tử của DATE_POLICIES
    route_type: str  # situational | direct | out_of_scope
    event_date: str | None
    direct_ref: dict | None  # {"law_id", "article"} cho câu direct
    queries: list[str]  # câu hỏi gốc rồi các truy vấn viết lại
    evidence: list[dict]  # chunk dùng làm ngữ cảnh, gộp qua các vòng
    n_rewrites: int
    sufficient: bool
    rewrite: bool
    answer: str
    insufficient: bool  # generate trả về INSUFFICIENT
    n_generations: int
    unsupported: list[str]  # câu mất hết căn cứ ở lần verify trước, đưa lại cho generate
    regenerate: bool
    removed: list[str]  # mã trích dẫn bị verify gỡ
    citations: list[dict]
    refused: bool
    refuse_reason: str
    trace: Annotated[list[dict], operator.add]  # mỗi nút nối thêm một bước


def initial_state(question, date_policy="event"):
    """Trạng thái ban đầu cho một câu hỏi (mặc định situational, chưa có bằng chứng, lọc hiệu lực theo `date_policy`)."""
    return {"question": question, "date_policy": date_policy, "route_type": "situational", "event_date": None,
            "direct_ref": None, "queries": [question], "evidence": [], "n_rewrites": 0, "n_generations": 0,
            "unsupported": [], "answer": "", "citations": [], "refused": False, "trace": []}
