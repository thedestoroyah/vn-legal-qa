"""Chạy tác tử: Agent.run(question, config) -> dict theo Phụ lục A.5.

CLI: python -m src.agent.run "câu hỏi" [--config full] [--variant clause_header] [--json]
"""
import argparse
import json

from src.agent.graph import build_graph
from src.agent.nodes import Deps
from src.agent.state import CONFIGS, DATE_POLICIES, initial_state
from src.ingestion.legal_chunker import LAWS_PATH


class Agent:
    """Tác tử hỏi đáp: giữ `deps` và đồ thị đã compile cho từng cấu hình."""

    def __init__(self, deps):
        self.deps = deps
        self._graphs = {}  # mỗi cấu hình compile một lần, dùng lại cho mọi câu hỏi

    def run(self, question, config="full", date_policy="event"):
        """Trả lời một câu hỏi.

        Args:
            question: câu hỏi pháp luật (tự bỏ khoảng trắng đầu cuối).
            config: một khóa của CONFIGS.
            date_policy: chính sách lọc hiệu lực (DATE_POLICIES); mặc định "event" = theo ngày của tình huống.

        Returns:
            dict theo Phụ lục A.5: answer, refused, citations, retrieved_chunks, trace.

        Raises:
            ValueError: config hoặc date_policy lạ, hoặc câu hỏi rỗng.
        """
        if config not in CONFIGS:
            raise ValueError(f"config phải thuộc {tuple(CONFIGS)}, nhận {config!r}")
        if date_policy not in DATE_POLICIES:
            raise ValueError(f"date_policy phải thuộc {DATE_POLICIES}, nhận {date_policy!r}")
        if not question or not question.strip():
            raise ValueError("câu hỏi rỗng")
        if config not in self._graphs:
            self._graphs[config] = build_graph(self.deps, config)
        return to_response(self._graphs[config].invoke(initial_state(question.strip(), date_policy)))


def to_response(state):
    """Đổi state cuối của đồ thị sang phản hồi Phụ lục A.5."""
    return {"answer": state["answer"], "refused": state["refused"], "citations": state["citations"],
            "retrieved_chunks": [{"chunk_id": c["chunk_id"], "score": c.get("score")} for c in state["evidence"]],
            "trace": state["trace"]}


def load_agent(variant="clause_header", cache_dir=None, max_retries=None, timeout=None):
    """Dựng Agent thật: LLM từ .env (LLM_*), Retriever trên biến thể đã nạp Chroma (tải mô hình, chậm lần đầu).

    Args:
        variant: biến thể chỉ mục (xem src.ingestion.index.VARIANTS).
        cache_dir: thư mục cache LLM; None dùng cache mặc định (đặt thư mục mới để đo latency không dùng cache).
        max_retries: số lần thử lại khi LLM lỗi 429/5xx; None theo biến môi trường LLM_MAX_RETRIES.
        timeout: giây chờ tối đa mỗi lượt gọi LLM; None theo mặc định của SDK.

    Returns:
        Agent sẵn sàng trả lời.
    """
    from src.generation.llm import CACHE_DIR, from_env
    from src.retrieval.retriever import load_retriever
    laws = json.loads(LAWS_PATH.read_text(encoding="utf-8"))
    return Agent(Deps(from_env("LLM", cache_dir or CACHE_DIR, max_retries=max_retries, timeout=timeout), load_retriever(variant), laws))

def print_result(out):
    """In câu trả lời, danh sách trích dẫn và các bước trace ra màn hình."""
    print(out["answer"])
    for c in out["citations"]:
        print(f"  [{c['chunk_id']}] {c['document']}, {c['article']}" + (f", {c['clause']}" if c["clause"] else ""))
    print("\nCác bước:")
    for step in out["trace"]:
        print(f"  {step['node']:<15}{step['ms']:>7} ms  {step['llm_calls']} LLM  "
              f"{json.dumps(step['output'], ensure_ascii=False)}")


def main(argv=None):
    """Điểm vào CLI."""
    parser = argparse.ArgumentParser(description="Hỏi tác tử pháp luật")
    parser.add_argument("question")
    parser.add_argument("--config", default="full", choices=list(CONFIGS))
    parser.add_argument("--variant", default="clause_header")
    parser.add_argument("--json", action="store_true", help="in nguyên phản hồi JSON (Phụ lục A.5)")
    args = parser.parse_args(argv)
    out = load_agent(args.variant).run(args.question, args.config)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print_result(out)


if __name__ == "__main__":
    main()
