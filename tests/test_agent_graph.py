import pytest

from src.agent.graph import build_graph
from src.agent.nodes import REFUSALS
from src.agent.state import CONFIGS, initial_state
from src.generation.prompts import INSUFFICIENT
from tests.agent_fakes import FakeRetriever, chunk, make_deps, nodes_called

A, B, C = "BLDS2015_Dieu357_Khoan1", "BLDS2015_Dieu357_Khoan2", "BLDS2015_Dieu468_Khoan1"
SIT = {"type": "situational", "event_date": None, "law_id": None, "article": None}
OK = {"sufficient": True, "new_query": None}
CLEAN = {"unsupported": []}


def run(deps, config="full"):
    return build_graph(deps, config).invoke(initial_state("câu hỏi"))


def path(state):
    return [step["node"] for step in state["trace"]]


def test_out_of_scope_refuses_without_retrieval(tmp_path):
    r = FakeRetriever()
    s = run(make_deps(tmp_path, r, route=[{**SIT, "type": "out_of_scope"}]))
    assert path(s) == ["route", "refuse"]
    assert s["refused"] is True and s["answer"] == REFUSALS["out_of_scope"]
    assert r.searches == []


def test_direct_question_looks_up_article(tmp_path):
    r = FakeRetriever(articles={"BLDS2015_Dieu357": chunk("BLDS2015_Dieu357")})
    d = make_deps(tmp_path, r, route=[{**SIT, "type": "direct", "law_id": "BLDS2015", "article": 357}],
                  generate=["Điều 357 quy định lãi chậm trả [BLDS2015_Dieu357]."], verify=[CLEAN])
    s = run(d)
    assert path(s) == ["route", "lookup_article", "generate", "verify"]
    assert [c["chunk_id"] for c in s["citations"]] == ["BLDS2015_Dieu357"]
    assert r.searches == []


def test_direct_with_unknown_article_falls_back_to_retrieval(tmp_path):
    r = FakeRetriever([[chunk(A)]])
    d = make_deps(tmp_path, r, route=[{**SIT, "type": "direct", "law_id": "BLDS2015", "article": 9999}],
                  grade=[OK], generate=[f"Có [{A}]."], verify=[CLEAN])
    assert path(run(d)) == ["route", "lookup_article", "retrieve", "grade", "generate", "verify"]


def test_rewrite_loop_stops_after_two_rewrites_then_refuses(tmp_path):
    r = FakeRetriever([[chunk(A)], [chunk(B)], [chunk(C)]])
    grades = [{"sufficient": False, "new_query": f"q{i}"} for i in (1, 2, 3)]
    s = run(make_deps(tmp_path, r, route=[SIT], grade=grades))
    assert path(s) == ["route", "retrieve", "grade", "retrieve", "grade", "retrieve", "grade", "refuse"]
    assert [x["query"] for x in r.searches] == ["câu hỏi", "q1", "q2"]
    assert s["answer"] == REFUSALS["insufficient"]
    assert [c["chunk_id"] for c in s["evidence"]] == [A, B, C]


def test_verify_removes_wrong_citation_and_regenerates_once(tmp_path):
    r = FakeRetriever([[chunk(A), chunk(B)]])
    d = make_deps(tmp_path, r, route=[SIT], grade=[OK],
                  generate=[f"Một [{A}]. Hai [{B}].", f"Một [{B}]. Hai [{B}]."],
                  verify=[{"unsupported": [{"sentence": 1, "chunk_id": A}]}, CLEAN])
    s = run(d)
    assert path(s) == ["route", "retrieve", "grade", "generate", "verify", "generate", "verify"]
    assert s["answer"] == f"Một [{B}]. Hai [{B}]."
    assert [c["chunk_id"] for c in s["citations"]] == [B]
    second_generate = [m for node, m in d.llm.client.seen if node == "generate"][1]
    assert f"- Một [{A}]." in second_generate[-1]["content"]


def test_event_before_any_law_refuses_without_more_llm_calls(tmp_path):
    r = FakeRetriever([[]])
    d = make_deps(tmp_path, r, route=[{**SIT, "event_date": "1990-07-01"}])
    s = run(d)
    assert path(s) == ["route", "retrieve", "refuse"]
    assert s["answer"] == REFUSALS["no_evidence"]
    assert r.searches[0]["date"] == "1990-07-01"
    assert nodes_called(d.llm) == ["route"]


def test_generate_sentinel_refuses(tmp_path):
    d = make_deps(tmp_path, FakeRetriever([[chunk(A)]]), route=[SIT], grade=[OK], generate=[INSUFFICIENT])
    s = run(d)
    assert path(s)[-2:] == ["generate", "refuse"]
    assert s["answer"] == REFUSALS["insufficient"] and s["citations"] == []


@pytest.mark.parametrize("config, expected", [
    ("baseline", ["retrieve", "generate", "verify"]),
    ("no_router", ["retrieve", "grade", "generate", "verify"]),
    ("no_grading", ["route", "retrieve", "generate", "verify"]),
    ("no_verify", ["route", "retrieve", "grade", "generate", "verify"]),
    ("full", ["route", "retrieve", "grade", "generate", "verify"]),
])
def test_configs_take_expected_paths(tmp_path, config, expected):
    r = FakeRetriever([[chunk(A)]])
    d = make_deps(tmp_path, r, route=[SIT], grade=[OK], generate=[f"Có [{A}]."], verify=[CLEAN])
    s = run(d, config)
    assert path(s) == expected
    assert ("verify" in nodes_called(d.llm)) == CONFIGS[config]["use_verify"]
    assert [c["chunk_id"] for c in s["citations"]] == [A]
    assert r.searches[0]["date"] is None


def test_trace_records_output_ms_and_llm_calls(tmp_path):
    d = make_deps(tmp_path, FakeRetriever([[chunk(A)]]), route=[SIT], grade=[OK], generate=[f"Có [{A}]."],
                  verify=[CLEAN])
    steps = {step["node"]: step for step in run(d)["trace"]}
    assert steps["route"]["llm_calls"] == 1 and steps["retrieve"]["llm_calls"] == 0
    assert steps["retrieve"]["output"] == {"queries": ["câu hỏi"], "evidence": [A]}
    assert steps["route"]["output"] == {"route_type": "situational", "event_date": None, "direct_ref": None}
    assert "answer" not in steps["generate"]["output"] and "citations" not in steps["verify"]["output"]
    assert all(isinstance(step["ms"], int) and step["ms"] >= 0 for step in steps.values())


def test_trace_ms_excludes_rate_limit_sleep(tmp_path):
    d = make_deps(tmp_path, FakeRetriever([[chunk(A)]]), route=[SIT], grade=[OK], generate=[f"Có [{A}]."],
                  verify=[CLEAN])
    d.llm.min_interval = 0.3  # lượt gọi thật thứ hai trở đi phải ngủ ~0.3 s
    steps = {step["node"]: step for step in run(d)["trace"]}
    assert steps["grade"]["ms"] < 150
