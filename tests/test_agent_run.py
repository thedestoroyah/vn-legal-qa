import pytest

from src.agent import run as run_module
from src.agent.run import Agent
from tests.agent_fakes import FakeRetriever, chunk, make_deps

A = "BLDS2015_Dieu357_Khoan1"
SIT = {"type": "situational", "event_date": None, "law_id": None, "article": None}


def agent(tmp_path, n=1):
    return Agent(make_deps(tmp_path, FakeRetriever([[chunk(A)]] * n), route=[SIT] * n,
                           grade=[{"sufficient": True, "new_query": None}] * n, generate=[f"Có [{A}]."] * n,
                           verify=[{"unsupported": []}] * n))


def test_run_returns_api_shape(tmp_path):
    out = agent(tmp_path).run("  câu hỏi  ", "full")
    assert set(out) == {"answer", "refused", "citations", "retrieved_chunks", "trace"}
    assert out["answer"] == f"Có [{A}]." and out["refused"] is False
    assert out["retrieved_chunks"] == [{"chunk_id": A, "score": 0.5}]
    assert out["citations"] == [{"chunk_id": A, "document": "Văn bản BLDS2015", "article": "Điều 357",
                                 "clause": "Khoản 1", "content": "nội dung"}]
    assert [s["node"] for s in out["trace"]] == ["route", "retrieve", "grade", "generate", "verify"]


@pytest.mark.parametrize("question, config", [("câu hỏi", "khác"), ("", "full"), ("   ", "full")])
def test_run_rejects_bad_input(tmp_path, question, config):
    with pytest.raises(ValueError):
        agent(tmp_path).run(question, config)


def test_run_compiles_each_config_once(tmp_path, monkeypatch):
    built = []
    real = run_module.build_graph
    monkeypatch.setattr(run_module, "build_graph", lambda deps, config: built.append(config) or real(deps, config))
    a = agent(tmp_path, n=2)
    a.run("câu một", "full")
    a.run("câu hai", "full")
    assert built == ["full"]


def test_cli_prints_answer_citation_and_trace(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(run_module, "load_agent", lambda variant: agent(tmp_path))
    run_module.main(["câu hỏi", "--config", "full"])
    out = capsys.readouterr().out
    assert f"Có [{A}]." in out and f"[{A}] Văn bản BLDS2015, Điều 357, Khoản 1" in out and "route" in out


def test_run_rejects_unknown_date_policy(tmp_path):
    with pytest.raises(ValueError):
        agent(tmp_path).run("câu hỏi", "full", "hôm qua")


def test_run_passes_date_policy_to_retrieval(tmp_path):
    a = agent(tmp_path)
    a.run("câu hỏi", "full", "any")
    from src.retrieval.filters import ANY_DATE
    assert a.deps.retriever.searches[0]["date"] == ANY_DATE
