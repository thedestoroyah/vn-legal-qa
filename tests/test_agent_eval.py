import json

import httpx
import openai
import pytest

from eval import agent_eval
from eval.agent_eval import (load_results, parse_run, report_rows, run_agent, score, select_cases, stratified,
                             to_markdown)
from eval.evaluate import summarize


def case(cid, source="zalo", kind="situational", gold=("BLDS2015_Dieu357",)):
    return {"id": cid, "source": source, "type": kind, "question": f"câu {cid}", "gold_citations": list(gold),
            "reference_answer": "đáp án"}


def response(cited=("BLDS2015_Dieu357_Khoan1",), refused=False):
    return {"answer": "x", "refused": refused, "citations": [{"chunk_id": c} for c in cited],
            "retrieved_chunks": [{"chunk_id": c, "score": 1.0} for c in cited],
            "trace": [{"node": "route", "output": {}, "ms": 10, "llm_calls": 1},
                      {"node": "verify", "output": {}, "ms": 5, "llm_calls": 1}]}


def rate_limit():
    resp = httpx.Response(429, request=httpx.Request("POST", "http://test"))
    return openai.RateLimitError("hết quota", response=resp, body=None)


class FakeAgent:
    """Trả `response()`; câu có id trong `fail` thì ném lỗi tương ứng. Ghi lại các lượt gọi."""

    def __init__(self, fail=None):
        self.fail = fail or {}
        self.calls = []

    def run(self, question, config="full", date_policy="event"):
        self.calls.append((question, config, date_policy))
        cid = question.removeprefix("câu ")
        if cid in self.fail:
            raise self.fail[cid]
        return response()


def test_parse_run_defaults_policy_to_event():
    assert parse_run("full") == ("full", "event")
    assert parse_run("full@any") == ("full", "any")


def test_select_cases_rq4_keeps_only_temporal():
    cases = [case("a"), case("b", kind="temporal")]
    assert [c["id"] for c in select_cases(cases, "rq4")] == ["b"]
    assert [c["id"] for c in select_cases(cases, "rq3", limit=1)] == ["a"]


def test_stratified_keeps_source_share_and_is_deterministic():
    cases = [case(f"z{i}") for i in range(60)] + [case(f"s{i}", "synthetic") for i in range(40)]
    picked = stratified(cases, 10)
    assert picked == stratified(cases, 10)
    assert sum(c["source"] == "zalo" for c in picked) == 6 and len(picked) == 10
    assert [c["id"] for c in picked] == [c["id"] for c in cases if c in picked]  # giữ thứ tự gốc


def test_run_agent_resumes_and_does_not_duplicate(tmp_path):
    out = tmp_path / "r.jsonl"
    cases = [case("a"), case("b")]
    assert run_agent(FakeAgent(), cases, ["full"], out) == 2
    agent = FakeAgent()
    assert run_agent(agent, cases, ["full", "full@any"], out) == 2
    assert [c[1:] for c in agent.calls] == [("full", "any"), ("full", "any")]
    assert len(load_results(out)) == 4


def test_run_agent_stops_on_rate_limit_and_records_other_errors(tmp_path):
    out = tmp_path / "r.jsonl"
    conn = openai.APIConnectionError(request=httpx.Request("POST", "http://test"))
    cases = [case("a"), case("b"), case("c"), case("d")]
    assert run_agent(FakeAgent(fail={"b": conn, "c": rate_limit()}), cases, ["full"], out) == 2
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert [(r["id"], "error" in r) for r in rows] == [("a", False), ("b", True)]
    assert set(load_results(out)) == {("a", "full")}  # dòng lỗi không tính là xong: lần sau chạy lại
    assert run_agent(FakeAgent(), cases, ["full"], out) == 3


def test_score_article_level_and_trace_totals():
    row = score(case("a", gold=("BLDS2015_Dieu357", "BLDS2015_Dieu468")), "full",
                response(cited=("BLDS2015_Dieu357_Khoan1", "BLDS2015_Dieu357_Khoan2", "LTM2005_Dieu306")))
    assert row["config"] == "full" and row["source"] == "zalo"
    assert (row["precision"], row["recall"]) == (0.5, 0.5)
    assert row["refusal_ok"] == 1.0 and row["version_ok"] is None
    assert (row["llm_calls"], row["ms"]) == (2, 15)


def test_score_temporal_version():
    row = score(case("t", kind="temporal", gold=("BLLD2012_Dieu22_Khoan1",)), "full@any",
                response(cited=("BLLD2019_Dieu20_Khoan1",)))
    assert row["version_ok"] == 0.0


def test_report_rows_merge_judge_and_skip_cases_outside_set():
    results = {("a", "full"): response(), ("x", "full"): response()}
    judged = {("a", "full"): {"faithfulness": 1.0, "correctness": 0.5}}
    rows = report_rows([case("a")], results, judged)
    assert len(rows) == 1 and (rows[0]["faithfulness"], rows[0]["correctness"]) == (1.0, 0.5)
    md = to_markdown(summarize(rows, agent_eval.METRICS))
    assert "| full | zalo | 1 |" in md and "| full | all | 1 |" in md


def test_report_rows_common_keeps_only_ids_present_in_every_run():
    results = {("a", "full"): response(), ("b", "full"): response(), ("a", "baseline"): response()}
    rows = report_rows([case("a"), case("b")], results, {}, common=True)
    assert sorted((r["id"], r["config"]) for r in rows) == [("a", "baseline"), ("a", "full")]


def test_subset_ids_are_frozen_in_file(tmp_path):
    path = tmp_path / "subset.json"
    cases = [case(f"z{i}") for i in range(60)] + [case(f"s{i}", "synthetic") for i in range(40)]
    first = agent_eval.subset_cases(cases, 10, path)
    more = cases + [case("m_new", "manual")]  # Hùng thêm câu: mẫu đã chốt không được đổi
    assert [c["id"] for c in agent_eval.subset_cases(more, 10, path)] == [c["id"] for c in first]


def test_score_reports_answered_flag():
    assert score(case("a"), "full", response(refused=True))["answered"] == 0.0
    assert score(case("a"), "full", response())["answered"] == 1.0


def test_report_warns_when_runs_cover_different_cases():
    rows = report_rows([case("a"), case("b")], {("a", "full"): response(), ("b", "full"): response(),
                                                ("a", "baseline"): response()}, {})
    md = to_markdown(summarize(rows, agent_eval.METRICS))
    assert "Cảnh báo" in md and "--common" in md


def test_cmd_run_passes_cache_dir(tmp_path, monkeypatch):
    seen = {}

    class Deps:
        llm = type("L", (), {"calls": 0, "requests": 0})()

    def fake_load(cache_dir=None):
        seen["cache_dir"] = cache_dir
        return type("A", (), {"deps": Deps, "run": lambda *a: response()})()

    import src.agent.run
    monkeypatch.setattr(src.agent.run, "load_agent", fake_load)
    monkeypatch.setattr(agent_eval, "CASES_PATH", tmp_path / "c.json")
    monkeypatch.setattr(agent_eval, "RESULTS_DIR", tmp_path)
    (tmp_path / "c.json").write_text(json.dumps([case("a")]), encoding="utf-8")
    agent_eval.main(["run", "--rq", "rq3", "--configs", "full", "--cache-dir", str(tmp_path / "fresh")])
    assert seen["cache_dir"] == str(tmp_path / "fresh")


def test_paired_diff_zero_when_runs_identical():
    rows = [{"id": i, "config": c, "recall": v} for i, v in enumerate([1.0, 0.0, 0.5]) for c in ("full", "x")]
    assert agent_eval.paired_diff(rows, "full", "recall") == {"x": (3, 0.0, 0.0, 0.0)}


def test_paired_diff_uses_only_cases_with_both_values_and_ci_brackets_mean():
    rows = ([{"id": i, "config": "full", "recall": 1.0} for i in range(20)]
            + [{"id": i, "config": "x", "recall": 0.0 if i < 10 else 1.0} for i in range(20)]
            + [{"id": 99, "config": "x", "recall": 0.0}, {"id": 98, "config": "full", "recall": None},
               {"id": 98, "config": "x", "recall": 1.0}])
    n, diff, lo, hi = agent_eval.paired_diff(rows, "full", "recall")["x"]
    assert (n, diff) == (20, -0.5) and lo <= -0.5 <= hi < 0
    assert agent_eval.paired_diff(rows, "full", "recall") == agent_eval.paired_diff(rows, "full", "recall")


def test_diff_markdown_marks_ci_excluding_zero():
    rows = ([{"id": i, "config": "full", **dict.fromkeys(agent_eval.CI_METRICS, 1.0)} for i in range(10)]
            + [{"id": i, "config": "x", **dict.fromkeys(agent_eval.CI_METRICS, 0.0)} for i in range(10)])
    md = agent_eval.diff_markdown(rows, "full")
    assert "| x | 10 | -1.000* [-1.000; -1.000] |" in md and "full" in md
    rows.append({"id": 0, "config": "y", **dict.fromkeys(agent_eval.CI_METRICS, 0.0), "version_ok": None})
    rows += [{"id": i, "config": "y", **dict.fromkeys(agent_eval.CI_METRICS, 0.0)} for i in range(1, 10)]
    assert "(n=9)" in agent_eval.diff_markdown(rows, "full")


def test_cmd_report_filters_configs_writes_out_and_appends_ci(tmp_path, monkeypatch):
    monkeypatch.setattr(agent_eval, "CASES_PATH", tmp_path / "c.json")
    monkeypatch.setattr(agent_eval, "RESULTS_DIR", tmp_path)
    (tmp_path / "c.json").write_text(json.dumps([case("a"), case("b")]), encoding="utf-8")
    for cid in ("a", "b"):
        for run in ("full", "baseline", "no_verify"):
            agent_eval.append_jsonl(tmp_path / "agent_rq3.jsonl", {"id": cid, "run": run, "response": response()})
    out = tmp_path / "full_vs_baseline.md"
    agent_eval.main(["report", "--rq", "rq3", "--configs", "full", "baseline", "--ci", "--out", str(out)])
    md = out.read_text(encoding="utf-8")
    assert "| baseline | all | 2 |" in md and "no_verify" not in md and "Chênh lệch so với `full`" in md
    assert not (tmp_path / "agent_rq3.md").exists()
