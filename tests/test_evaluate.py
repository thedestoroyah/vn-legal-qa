from eval.evaluate import CONFIGS, eval_case, run, summarize, to_markdown


class FakeRetriever:
    def __init__(self, chunks):
        self.chunks, self.calls = chunks, []

    def search(self, query, k=5, date=None, mode="hybrid_rerank"):
        self.calls.append((query, k, date, mode))
        return self.chunks[:k]


CHUNKS = [{"chunk_id": "BLDS2015_Dieu321_Khoan2", "law_id": "BLDS2015"},
          {"chunk_id": "LDN2020_Dieu1", "law_id": "LDN2020"},
          {"chunk_id": "BLDS2015_Dieu321_Khoan1", "law_id": "BLDS2015"}]


def case(cid, gold, source):
    return {"id": cid, "question": "q", "type": "situational", "domain": "dan_su", "event_date": None,
            "gold_citations": gold, "source": source}


def test_eval_case_article_and_clause_levels():
    row = eval_case(FakeRetriever(CHUNKS), case("S1", ["BLDS2015_Dieu321_Khoan1"], "synthetic"), "bm25", True)
    assert (row["hit5"], row["mrr10"], row["drm5"]) == (1.0, 1.0, 1 / 3)
    assert row["hit5_clause"] == 1.0 and row["mrr10_clause"] == 1 / 3


def test_clause_metrics_skipped_for_article_gold_or_non_clause_variant():
    zalo = eval_case(FakeRetriever(CHUNKS), case("Z1", ["BLDS2015_Dieu321"], "zalo"), "bm25", True)
    assert zalo["hit5"] == 1.0 and zalo["hit5_clause"] is None
    other = eval_case(FakeRetriever(CHUNKS), case("S1", ["BLDS2015_Dieu321_Khoan1"], "synthetic"), "bm25", False)
    assert other["hit5_clause"] is None


def test_run_summarize_and_markdown():
    cases = [case("Z1", ["BLDS2015_Dieu321"], "zalo"), case("S1", ["LDN2020_Dieu9"], "synthetic")]
    fake = FakeRetriever(CHUNKS)
    rows = run("rq1", cases, lambda variant: fake)
    assert len(rows) == len(CONFIGS["rq1"]) * 2 and rows[0]["config"] == "clause_header/bm25"
    summary = {(s["config"], s["source"]): s for s in summarize(rows)}
    assert summary[("clause_header/bm25", "all")]["n"] == 2
    assert summary[("clause_header/bm25", "all")]["hit5"] == 0.5
    assert summary[("clause_header/bm25", "zalo")]["hit5_clause"] is None
    md = to_markdown(summarize(rows))
    assert md.splitlines()[0].startswith("| config | source | n | Hit@5")
    assert "| clause_header/bm25 | zalo | 1 | 1.000 |" in md and "–" in md
