"""Đồ thị LangGraph của tác tử (spec mục 5) và 5 cấu hình RQ3; mỗi nút ghi một bước trace."""
import time
from functools import partial

from langgraph.graph import END, START, StateGraph

from src.agent import nodes
from src.agent.state import CONFIGS, AgentState

_BULKY = ("evidence", "answer", "citations")


def _summary(update):
    """Đầu ra gọn cho trace: bỏ văn bản dài, bằng chứng chỉ giữ chunk_id."""
    out = {k: v for k, v in update.items() if k not in _BULKY}
    if "evidence" in update:
        out["evidence"] = [c["chunk_id"] for c in update["evidence"]]
    return out


def _traced(name, fn, deps):
    """Bọc một nút: đo thời gian, đếm lượt gọi LLM (`llm_calls`, gồm cả trúng cache; `api_calls`, chỉ lượt gọi
    API thật) và nối một bước vào `trace`."""
    def step(state):
        calls, api, waited, start = deps.llm.requests, deps.llm.calls, deps.llm.waited, time.perf_counter()
        update = fn(state, deps)
        # trừ thời gian ngủ giãn cách RPM: latency của RQ3 phải phản ánh hệ thống, không phải giới hạn free tier
        elapsed = time.perf_counter() - start - (deps.llm.waited - waited)
        record = {"node": name, "output": _summary(update), "ms": max(0, round(elapsed * 1000)),
                  "llm_calls": deps.llm.requests - calls, "api_calls": deps.llm.calls - api}
        return {**update, "trace": [record]}
    return step


def _after_route(state):
    if state["route_type"] == "out_of_scope":
        return "refuse"
    return "lookup_article" if state["route_type"] == "direct" and state["direct_ref"] else "retrieve"


def _after_grade(state):
    if state["sufficient"]:
        return "generate"
    return "retrieve" if state["rewrite"] else "refuse"


def build_graph(deps, config="full"):
    """Dựng và compile đồ thị cho một cấu hình.

    Args:
        deps: nodes.Deps (LLM, Retriever, laws).
        config: một khóa của CONFIGS (baseline, full, no_router, no_grading, no_verify).

    Returns:
        Đồ thị đã compile; `.invoke(initial_state(câu_hỏi))` trả state cuối kèm `trace`.

    Raises:
        KeyError: config không hợp lệ.
    """
    flags = CONFIGS[config]
    steps = {"route": nodes.route, "lookup_article": nodes.lookup_article, "retrieve": nodes.retrieve,
             "grade": nodes.grade, "generate": nodes.generate, "refuse": nodes.refuse,
             "verify": partial(nodes.verify, use_llm=flags["use_verify"])}
    graph = StateGraph(AgentState)
    for name, fn in steps.items():
        graph.add_node(name, _traced(name, fn, deps))
    # nút bị cấu hình tắt (route, grade) vẫn có trong đồ thị nhưng không có cạnh nào dẫn tới
    graph.add_conditional_edges(START, lambda s: "route" if flags["use_router"] else "retrieve")
    graph.add_conditional_edges("route", _after_route)
    graph.add_conditional_edges("lookup_article", lambda s: "generate" if s["evidence"] else "retrieve")
    graph.add_conditional_edges(
        "retrieve", lambda s: "refuse" if not s["evidence"] else "grade" if flags["use_grading"] else "generate")
    graph.add_conditional_edges("grade", _after_grade)
    graph.add_conditional_edges("generate", lambda s: "refuse" if s["insufficient"] else "verify")
    graph.add_conditional_edges("verify", lambda s: "generate" if s["regenerate"] else END)
    graph.add_edge("refuse", END)
    return graph.compile()
