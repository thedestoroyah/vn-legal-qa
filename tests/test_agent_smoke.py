from eval.agent_smoke import EXTRA, pick_cases, summarize


def case(cid, source, type_="situational", gold=("BLDS2015_Dieu357",)):
    return {"id": cid, "source": source, "type": type_, "question": cid, "gold_citations": list(gold)}


def test_pick_cases_fills_missing_manual_with_extra():
    cases = [case(f"z{i}", "zalo") for i in range(5)] + [case(f"s{i}", "synthetic") for i in range(5)]
    picked = pick_cases(cases)
    assert [c["id"] for c in picked] == ["z0", "z1", "z2", "s0", "s1", "s2"] + [c["id"] for c in EXTRA[:4]]


def test_pick_cases_prefers_non_situational_manual():
    cases = [case("m_sit", "manual"), case("m_tmp", "manual", "temporal")]
    assert [c["id"] for c in pick_cases(cases)] == ["m_tmp", "m_sit"] + [c["id"] for c in EXTRA[:2]]


def test_summarize_scores_at_article_level():
    out = {"refused": False, "citations": [{"chunk_id": "BLDS2015_Dieu357_Khoan2"}],
           "trace": [{"node": "route", "output": {"route_type": "situational"}, "ms": 5, "llm_calls": 1},
                     {"node": "verify", "output": {}, "ms": 7, "llm_calls": 1}]}
    row = summarize(case("z", "zalo"), out)
    assert row == {"id": "z", "type": "situational", "route": "situational", "refused": False,
                   "cited": ["BLDS2015_Dieu357"], "gold": ["BLDS2015_Dieu357"], "hit": True, "llm_calls": 2, "ms": 12}


def test_summarize_refused_out_of_scope_counts_as_hit():
    out = {"refused": True, "citations": [], "trace": []}
    row = summarize(case("x", "manual", "out_of_scope", gold=()), out)
    assert row["hit"] is True and row["route"] == "-"
