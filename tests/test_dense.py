from src.ingestion.index import build_index
from src.retrieval.dense import DenseIndex


def fake_embed(texts):
    return [[float("lãi" in t), float("phạt" in t), 1.0] for t in texts]


def chunk(cid, content, eff, expiry=None):
    return {"chunk_id": cid, "law_id": "A", "document": "Luật A", "chapter": None, "section": None,
            "article": "Điều 1", "article_title": "T", "clause": None, "point": None, "content": content,
            "effective_date": eff, "expiry_date": expiry, "status": "x"}


CHUNKS = [chunk("OLD", "trả lãi", "2013-01-01", "2021-01-01"), chunk("NEW", "trả lãi chậm", "2021-01-01"),
          chunk("PHAT", "bị phạt", "2017-01-01")]


def test_dense_ranks_by_similarity_and_filters_validity(tmp_path):
    dense = DenseIndex(build_index(CHUNKS, fake_embed, tmp_path), fake_embed)
    hits = dense.search("lãi", k=5)
    assert [cid for cid, _ in hits] == ["NEW", "PHAT"]
    assert hits[0][1] > hits[1][1]
    assert [cid for cid, _ in dense.search("lãi", k=5, date="2020-06-01")] == ["OLD", "PHAT"]


def test_dense_k_larger_than_matches_returns_fewer(tmp_path):
    dense = DenseIndex(build_index(CHUNKS, fake_embed, tmp_path), fake_embed)
    assert dense.search("lãi", k=50, date="2010-01-01") == []


def test_dense_any_date_returns_all_versions(tmp_path):
    from src.retrieval.filters import ANY_DATE
    dense = DenseIndex(build_index(CHUNKS, fake_embed, tmp_path), fake_embed)
    assert {cid for cid, _ in dense.search("lãi", k=5, date=ANY_DATE)} == {"OLD", "NEW", "PHAT"}
