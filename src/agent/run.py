"""Chạy tác tử: Agent.run(question, config) -> dict theo Phụ lục A.5.

CLI: python -m src.agent.run "câu hỏi" [--config full] [--variant clause_header] [--json]
"""
import argparse
import json

from src.agent.graph import build_graph
from src.agent.nodes import Deps
from src.agent.state import CONFIGS, initial_state
from src.ingestion.legal_chunker import LAWS_PATH


class Agent:
    """Tác tử hỏi đáp: giữ `deps` và đồ thị đã compile cho từng cấu hình."""

    def __init__(self, deps):
        self.deps = deps
        self._graphs = {}  # mỗi cấu hình compile một lần, dùng lại cho mọi câu hỏi

    def run(self, question, config="full"):
        """Trả lời một câu hỏi.

        Args:
            question: câu hỏi pháp luật (tự bỏ khoảng trắng đầu cuối).
            config: một khóa của CONFIGS.

        Returns:
            dict theo Phụ lục A.5: answer, refused, citations, retrieved_chunks, trace.

        Raises:
            ValueError: config lạ hoặc câu hỏi rỗng.
        """
        if config not in CONFIGS:
            raise ValueError(f"config phải thuộc {tuple(CONFIGS)}, nhận {config!r}")
        if not question or not question.strip():
            raise ValueError("câu hỏi rỗng")
        if config not in self._graphs:
            self._graphs[config] = build_graph(self.deps, config)
        return to_response(self._graphs[config].invoke(initial_state(question.strip())))


def to_response(state):
    """Đổi state cuối của đồ thị sang phản hồi Phụ lục A.5."""
    return {"answer": state["answer"], "refused": state["refused"], "citations": state["citations"],
            "retrieved_chunks": [{"chunk_id": c["chunk_id"], "score": c.get("score")} for c in state["evidence"]],
            "trace": state["trace"]}


def load_agent(variant="clause_header"):
    """Dựng Agent thật: LLM từ .env (LLM_*), Retriever trên biến thể đã nạp Chroma (tải mô hình, chậm lần đầu)."""
    from src.generation.llm import from_env
    from src.retrieval.retriever import load_retriever
    laws = json.loads(LAWS_PATH.read_text(encoding="utf-8"))
    return Agent(Deps(from_env("LLM"), load_retriever(variant), laws))


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
