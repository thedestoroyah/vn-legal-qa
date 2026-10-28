import pytest

from src.agent import nodes
from src.agent.nodes import REFUSALS
from src.agent.state import initial_state
from tests.agent_fakes import FakeRetriever, chunk, make_deps

A, B = "BLDS2015_Dieu357_Khoan1", "BLDS2015_Dieu357_Khoan2"


def routed(tmp_path, **out):
    reply = {"type": "situational", "event_date": None, "law_id": None, "article": None, **out}
    return nodes.route(initial_state("q"), make_deps(tmp_path, route=[reply]))


def test_route_situational_with_event_date(tmp_path):
    assert routed(tmp_path, event_date="2020-07-01") == {
        "route_type": "situational", "event_date": "2020-07-01", "direct_ref": None}


@pytest.mark.parametrize("law, article, ref", [
    ("BLDS2015", 357, {"law_id": "BLDS2015", "article": "357"}),
    ("BLLĐ 2012", "Điều 22", {"law_id": "BLLD2012", "article": "22"}),
    ("blds-2015", "357", {"law_id": "BLDS2015", "article": "357"}),
    ("Bộ luật Dân sự", 357, None),  # không khớp mã nào: rơi về truy xuất thường
    ("BLDS2015", None, None),
])
def test_route_direct_normalizes_law_id_and_article(tmp_path, law, article, ref):
    assert routed(tmp_path, type="direct", law_id=law, article=article)["direct_ref"] == ref


@pytest.mark.parametrize("raw", ["2020", "năm 2020", "", 2020, "01/03/2020"])
def test_route_drops_malformed_event_date(tmp_path, raw):
    assert routed(tmp_path, event_date=raw)["event_date"] is None


def test_route_normalizes_compact_date(tmp_path):
    assert routed(tmp_path, event_date="20200301")["event_date"] == "2020-03-01"


def test_route_unknown_type_defaults_to_situational(tmp_path):
    assert routed(tmp_path, type="temporal")["route_type"] == "situational"


def test_route_broken_json_defaults_to_situational(tmp_path):
    out = nodes.route(initial_state("q"), make_deps(tmp_path, route=["không", "vẫn không"]))
    assert out == {"route_type": "situational", "event_date": None, "direct_ref": None}


def test_lookup_article_returns_article_as_evidence(tmp_path):
    art = chunk("BLDS2015_Dieu357")
    r = FakeRetriever(articles={"BLDS2015_Dieu357": art})
    state = {**initial_state("q"), "direct_ref": {"law_id": "BLDS2015", "article": "357"}}
    assert nodes.lookup_article(state, make_deps(tmp_path, r)) == {"evidence": [art]}
    assert r.lookups == [("BLDS2015", "357")]


def test_lookup_article_missing_returns_empty_evidence(tmp_path):
    state = {**initial_state("q"), "direct_ref": {"law_id": "BLDS2015", "article": "9999"}}
    assert nodes.lookup_article(state, make_deps(tmp_path)) == {"evidence": []}


def test_retrieve_uses_latest_query_and_event_date(tmp_path):
    r = FakeRetriever([[chunk(A)]])
    state = {**initial_state("câu gốc"), "queries": ["câu gốc", "truy vấn mới"], "event_date": "2020-07-01"}
    out = nodes.retrieve(state, make_deps(tmp_path, r))
    assert r.searches == [{"query": "truy vấn mới", "k": 5, "date": "2020-07-01"}]
    assert [c["chunk_id"] for c in out["evidence"]] == [A]


def test_retrieve_merges_previous_evidence_without_duplicates(tmp_path):
    r = FakeRetriever([[chunk(A), chunk(B)]])
    state = {**initial_state("q"), "evidence": [chunk(A)]}
    assert [c["chunk_id"] for c in nodes.retrieve(state, make_deps(tmp_path, r))["evidence"]] == [A, B]


@pytest.mark.parametrize("state, reason", [
    ({"route_type": "out_of_scope"}, "out_of_scope"),
    ({"evidence": []}, "no_evidence"),
    ({"evidence": [{"chunk_id": A}]}, "insufficient"),
])
def test_refuse_picks_reason_from_state(tmp_path, state, reason):
    out = nodes.refuse({**initial_state("q"), **state}, make_deps(tmp_path))
    assert out == {"answer": REFUSALS[reason], "refused": True, "citations": [], "refuse_reason": reason}

from src.generation.citations import NO_BASIS
from src.generation.prompts import INSUFFICIENT
from tests.agent_fakes import nodes_called


def with_evidence(**kw):
    return {**initial_state("q"), "evidence": [chunk(A)], **kw}


def test_grade_sufficient(tmp_path):
    d = make_deps(tmp_path, grade=[{"sufficient": True, "new_query": None}])
    assert nodes.grade(with_evidence(), d) == {"sufficient": True, "rewrite": False}


def test_grade_insufficient_appends_new_query(tmp_path):
    d = make_deps(tmp_path, grade=[{"sufficient": False, "new_query": "lãi chậm trả"}])
    assert nodes.grade(with_evidence(), d) == {
        "sufficient": False, "rewrite": True, "queries": ["q", "lãi chậm trả"], "n_rewrites": 1}


def test_grade_stops_after_max_rewrites(tmp_path):
    d = make_deps(tmp_path, grade=[{"sufficient": False, "new_query": "khác"}])
    assert nodes.grade(with_evidence(n_rewrites=2), d) == {"sufficient": False, "rewrite": False}


@pytest.mark.parametrize("new_query", ["q", "", None])
def test_grade_repeated_or_empty_query_does_not_loop(tmp_path, new_query):
    d = make_deps(tmp_path, grade=[{"sufficient": False, "new_query": new_query}])
    assert nodes.grade(with_evidence(), d) == {"sufficient": False, "rewrite": False}


@pytest.mark.parametrize("flag", ["false", "False", 0])
def test_grade_reads_string_false(tmp_path, flag):
    d = make_deps(tmp_path, grade=[{"sufficient": flag, "new_query": "khác"}])
    assert nodes.grade(with_evidence(), d)["rewrite"] is True


def test_grade_broken_json_defaults_to_sufficient(tmp_path):
    d = make_deps(tmp_path, grade=["không", "không"])
    assert nodes.grade(with_evidence(), d) == {"sufficient": True, "rewrite": False}


def test_generate_returns_answer_and_counts(tmp_path):
    d = make_deps(tmp_path, generate=[f"Trả lời: Có [{A}]."])
    assert nodes.generate(with_evidence(), d) == {"answer": f"Có [{A}].", "insufficient": False, "n_generations": 1}


@pytest.mark.parametrize("reply", [INSUFFICIENT, f"Trả lời: {INSUFFICIENT}", ""])
def test_generate_sentinel_or_empty_means_insufficient(tmp_path, reply):
    d = make_deps(tmp_path, generate=[reply])
    assert nodes.generate(with_evidence(), d)["insufficient"] is True


def test_generate_passes_event_date_and_feedback(tmp_path):
    d = make_deps(tmp_path, generate=[f"Có [{A}]."])
    nodes.generate(with_evidence(event_date="2020-07-01", unsupported=["Câu sai."]), d)
    user = d.llm.client.seen[0][1][-1]["content"]
    assert "Sự việc xảy ra ngày 2020-07-01." in user and "- Câu sai." in user


def test_verify_a_only_removes_unknown_ids_and_labels_lost_sentence(tmp_path):
    d = make_deps(tmp_path)
    out = nodes.verify(with_evidence(answer=f"Một [{A}]. Hai [BLDS2015_Dieu999].", n_generations=1), d, use_llm=False)
    assert out["answer"] == f"Một [{A}]. Hai {NO_BASIS}."
    assert out["removed"] == ["BLDS2015_Dieu999"]
    assert [c["chunk_id"] for c in out["citations"]] == [A]
    assert out["citations"][0] == {"chunk_id": A, "document": "Văn bản BLDS2015", "article": "Điều 357",
                                   "clause": "Khoản 1", "content": "nội dung"}
    assert out["regenerate"] is False and nodes_called(d.llm) == []


def test_verify_llm_removes_unsupported_pair_and_requests_regeneration(tmp_path):
    d = make_deps(tmp_path, verify=[{"unsupported": [{"sentence": 1, "chunk_id": A}, {"sentence": 2, "chunk_id": A}]}])
    state = with_evidence(evidence=[chunk(A), chunk(B)], answer=f"Một [{A}]. Hai [{A}, {B}]. Ba [{B}].",
                          n_generations=1)
    out = nodes.verify(state, d)
    assert out["regenerate"] is True
    assert out["unsupported"] == [f"Một [{A}]."]
    assert out["answer"] == f"Một. Hai [{B}]. Ba [{B}]."


def test_verify_after_regeneration_labels_instead_of_looping(tmp_path):
    d = make_deps(tmp_path, verify=[{"unsupported": [{"sentence": 1, "chunk_id": A}]}])
    state = with_evidence(evidence=[chunk(A), chunk(B)], answer=f"Một [{A}]. Hai [{B}].", n_generations=2)
    out = nodes.verify(state, d)
    assert out["regenerate"] is False
    assert out["answer"] == f"Một {NO_BASIS}. Hai [{B}]."
    assert [c["chunk_id"] for c in out["citations"]] == [B]


def test_verify_ignores_malformed_verdict_items(tmp_path):
    junk = [{"sentence": "1", "chunk_id": B}, {"sentence": 9, "chunk_id": A}, {"sentence": 0, "chunk_id": A},
            "rác", {"sentence": "x"}, {"sentence": "2", "chunk_id": A}]
    d = make_deps(tmp_path, verify=[{"unsupported": junk}])
    state = with_evidence(evidence=[chunk(A), chunk(B)], answer=f"Một [{A}]. Hai [{A}, {B}].", n_generations=1)
    out = nodes.verify(state, d)
    assert out["answer"] == f"Một [{A}]. Hai [{B}]."
    assert out["regenerate"] is False


def test_verify_broken_json_keeps_answer(tmp_path):
    d = make_deps(tmp_path, verify=["không", "không"])
    out = nodes.verify(with_evidence(answer=f"Có [{A}].", n_generations=1), d)
    assert out["answer"] == f"Có [{A}]." and out["removed"] == []


def test_verify_answer_without_any_citation_gets_note(tmp_path):
    d = make_deps(tmp_path)
    out = nodes.verify(with_evidence(answer="Có.", n_generations=1), d)
    assert out["answer"] == f"Có.\n\n{nodes.NO_CITATION_NOTE}"
    assert out["citations"] == [] and nodes_called(d.llm) == []


def test_lookup_article_ignores_law_not_in_force_at_event_date(tmp_path):
    art = {**chunk("BLLD2019_Dieu35"), "effective_date": "2021-01-01", "expiry_date": None}
    r = FakeRetriever(articles={"BLLD2019_Dieu35": art})
    state = {**initial_state("q"), "event_date": "1990-07-01", "direct_ref": {"law_id": "BLLD2019", "article": "35"}}
    assert nodes.lookup_article(state, make_deps(tmp_path, r)) == {"evidence": []}


@pytest.mark.parametrize("article, expected", [("Khoản 2 Điều 35", "35"), ("Điều 50A", "50a"), ("35", "35")])
def test_route_direct_prefers_number_after_dieu(tmp_path, article, expected):
    ref = routed(tmp_path, type="direct", law_id="BLLD2019", article=article)["direct_ref"]
    assert ref == {"law_id": "BLLD2019", "article": expected}


def test_verify_accepts_clause_citation_of_article_level_evidence(tmp_path):
    d = make_deps(tmp_path, verify=[{"unsupported": []}])
    art = chunk("BLDS2015_Dieu357")
    out = nodes.verify({**initial_state("q"), "evidence": [art], "answer": "Có [BLDS2015_Dieu357_Khoan1].",
                        "n_generations": 1}, d)
    assert out["answer"] == "Có [BLDS2015_Dieu357]." and out["removed"] == []
    assert [c["chunk_id"] for c in out["citations"]] == ["BLDS2015_Dieu357"]


from src.retrieval.filters import ANY_DATE


@pytest.mark.parametrize("policy, expected", [("event", "2020-07-01"), ("current", None), ("any", ANY_DATE)])
def test_retrieve_date_follows_policy(tmp_path, policy, expected):
    r = FakeRetriever([[chunk(A)]])
    state = {**initial_state("q", date_policy=policy), "event_date": "2020-07-01"}
    nodes.retrieve(state, make_deps(tmp_path, r))
    assert r.searches[0]["date"] == expected


def test_lookup_article_any_policy_ignores_validity(tmp_path):
    art = {**chunk("BLLD2019_Dieu35"), "effective_date": "2021-01-01", "expiry_date": None}
    r = FakeRetriever(articles={"BLLD2019_Dieu35": art})
    state = {**initial_state("q", date_policy="any"), "event_date": "1990-07-01",
             "direct_ref": {"law_id": "BLLD2019", "article": "35"}}
    assert nodes.lookup_article(state, make_deps(tmp_path, r)) == {"evidence": [art]}


@pytest.mark.parametrize("kind", [["direct"], {"a": 1}, 3])
def test_route_non_string_type_defaults_to_situational(tmp_path, kind):
    assert routed(tmp_path, type=kind)["route_type"] == "situational"
