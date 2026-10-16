import pytest

import json

from src.ingestion.index import build_index
from src.retrieval import retriever as retriever_module
from src.retrieval.retriever import CANDIDATES, RERANK_TOP, Retriever, load_retriever, rrf


class FakeIndex:
    def __init__(self, ranked):
        self.ranked, self.calls = ranked, []

    def search(self, query, k=50, date=None):
        self.calls.append((query, k, date))
        return self.ranked[:k]


def chunk(cid, content="x", clause=None):
    return {"chunk_id": cid, "law_id": "BLDS2015", "document": "Bộ luật Dân sự 2015", "article": "Điều 1",
            "article_title": "T", "clause": clause, "content": content}


CHUNKS = [chunk("a", "aa"), chunk("b", "b"), chunk("c", "cccc")]


def make(bm25=(("a", 5.0), ("b", 3.0)), dense=(("b", 0.9), ("c", 0.8)), rerank=None):
    return Retriever(CHUNKS, FakeIndex(list(bm25)), FakeIndex(list(dense)), rerank)


def test_rrf_scores():
    fused = dict(rrf([["a", "b"], ["b", "c"]], k=60))
    assert list(rrf([["a", "b"], ["b", "c"]], k=60))[0][0] == "b"
    assert fused["b"] == pytest.approx(1 / 62 + 1 / 61)
    assert fused["c"] == pytest.approx(1 / 62)


def test_hybrid_fuses_both_branches_and_passes_normalized_date():
    r = make()
    hits = r.search("q", k=2, date="20200301", mode="hybrid")
    assert [h["chunk_id"] for h in hits] == ["b", "a"]
    assert r.bm25.calls == [("q", CANDIDATES, "2020-03-01")] and r.dense.calls == [("q", CANDIDATES, "2020-03-01")]


def test_single_branch_modes_pass_k():
    r = make()
    assert [h["chunk_id"] for h in r.search("q", k=1, mode="bm25")] == ["a"]
    assert [h["chunk_id"] for h in r.search("q", k=1, mode="dense")] == ["b"]
    assert r.search("q", k=1, mode="bm25")[0]["score"] == 5.0


def test_rerank_reorders_candidates_using_header_text():
    seen = []

    def rerank(query, texts):
        seen.extend(texts)
        return [len(t) for t in texts]

    hits = make(rerank=rerank).search("q", k=3)
    assert [h["chunk_id"] for h in hits] == ["c", "a", "b"]
    assert all(t.startswith("Bộ luật Dân sự 2015 - Điều 1 - T\n") for t in seen)
    assert len(seen) <= RERANK_TOP


def test_errors_and_empty_query():
    r = make()
    with pytest.raises(ValueError):
        r.search("q", mode="vector")
    with pytest.raises(ValueError):
        r.search("q", date="2020")
    with pytest.raises(RuntimeError, match="reranker"):
        r.search("q")
    fresh = make()
    assert fresh.search("   ") == [] and fresh.bm25.calls == [] and fresh.dense.calls == []


def test_stale_index_gives_rebuild_hint():
    r = make(dense=(("ghost", 0.9),))
    with pytest.raises(RuntimeError, match="--rebuild"):
        r.search("q", mode="dense")


def test_get_article_joins_clauses_and_ignores_prefix_lookalikes():
    chunks = [chunk("BLDS2015_Dieu357_Khoan1", "A", "Khoản 1"), chunk("BLDS2015_Dieu3570_Khoan1", "Z", "Khoản 1"),
              chunk("BLDS2015_Dieu357_Khoan2", "B", "Khoản 2")]
    r = Retriever(chunks, FakeIndex([]), FakeIndex([]))
    article = r.get_article("BLDS2015", 357)
    assert (article["chunk_id"], article["content"]) == ("BLDS2015_Dieu357", "1. A\n2. B")
    assert r.get_article("BLDS2015", "999") is None


def test_hybrid_rerank_keeps_unreranked_tail_so_depth_matches_other_modes():
    ids = [f"c{i:02d}" for i in range(RERANK_TOP + 5)]
    chunks = [chunk(cid, cid) for cid in ids]
    ranking = [(cid, 1.0 / (i + 1)) for i, cid in enumerate(ids)]
    r = Retriever(chunks, FakeIndex(ranking), FakeIndex(ranking), rerank=lambda q, texts: [-i for i in range(len(texts))][::-1])
    hits = r.search("q", k=len(ids), mode="hybrid_rerank")
    assert len(hits) == len(ids)  # trước đây chỉ trả RERANK_TOP, làm Recall@k so lệch giữa các chế độ
    assert [h["chunk_id"] for h in hits[:RERANK_TOP]] == ids[:RERANK_TOP][::-1]
    assert [h["chunk_id"] for h in hits[RERANK_TOP:]] == ids[RERANK_TOP:]


def test_rerank_uses_the_variant_text_not_always_the_header():
    seen = []
    r = Retriever(CHUNKS, FakeIndex([("a", 1.0)]), FakeIndex([("b", 1.0)]),
                  rerank=lambda q, texts: seen.extend(texts) or [0.0] * len(texts), text_fn=lambda c: c["content"])
    r.search("q", k=2)
    assert sorted(seen) == ["aa", "b"]


@pytest.mark.parametrize("mode", ["bm25", "dense", "hybrid", "hybrid_rerank"])
def test_punctuation_only_query_touches_no_index(mode):
    r = make(rerank=lambda q, t: [0.0] * len(t))
    assert r.search("?! ...", mode=mode) == []
    assert r.bm25.calls == [] and r.dense.calls == []


def test_stale_candidate_under_rerank_gives_rebuild_hint():
    r = make(dense=(("ghost", 0.9),), rerank=lambda q, t: [0.0] * len(t))
    with pytest.raises(RuntimeError, match="--rebuild"):
        r.search("q")


def test_load_retriever_rejects_index_with_different_chunk_count(tmp_path, monkeypatch):
    rows = [{**chunk(f"A_Dieu{i}", text), "law_id": "A", "chapter": None, "section": None, "clause": None, "point": None,
             "effective_date": "2017-01-01", "expiry_date": None, "status": "x"}
            for i, text in ((1, "x"), (2, "y"), (3, "z"))]  # 3 chunk: với 2 chunk IDF của BM25 bằng 0
    monkeypatch.setattr(retriever_module, "PROCESSED_DIR", tmp_path)
    (tmp_path / "chunks.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    embed = lambda texts: [[1.0, 0.0] for _ in texts]
    rerank = lambda q, t: [0.0] * len(t)
    build_index(rows[:2], embed, tmp_path / "db")
    with pytest.raises(RuntimeError, match="--rebuild"):
        load_retriever("clause_header", embed=embed, rerank=rerank, db_path=tmp_path / "db")
    build_index(rows, embed, tmp_path / "db")
    hits = load_retriever("clause_header", embed=embed, rerank=rerank, db_path=tmp_path / "db").search("x", mode="bm25")
    assert [h["chunk_id"] for h in hits] == ["A_Dieu1"]
