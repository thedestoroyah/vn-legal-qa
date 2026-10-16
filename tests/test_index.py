import json

import chromadb

from src.ingestion.index import build_index, chunk_metadata, embedding_text

CHUNKS = [
    {"chunk_id": "A_Dieu1_Khoan1", "law_id": "A", "document": "Luật A", "chapter": "Chương I",
     "section": None, "article": "Điều 1", "article_title": "Lãi", "clause": "Khoản 1",
     "point": None, "content": "trả lãi", "effective_date": "2020-01-01", "status": "Còn hiệu lực"},
    {"chunk_id": "A_Dieu2", "law_id": "A", "document": "Luật A", "chapter": "Chương I",
     "section": None, "article": "Điều 2", "article_title": "Phạt", "clause": None,
     "point": None, "content": "bị phạt", "effective_date": "2020-01-01", "status": "Còn hiệu lực"},
]


def fake_embed(texts):
    return [[float(len(t)), 1.0] for t in texts]


def test_embedding_text_includes_hierarchy_context():
    text = embedding_text(CHUNKS[0])
    assert "Luật A" in text and "Điều 1" in text and "Lãi" in text and "trả lãi" in text


def test_build_index_stores_content_and_metadata_without_none(tmp_path):
    build_index(CHUNKS, fake_embed, tmp_path)
    col = chromadb.PersistentClient(path=str(tmp_path)).get_collection("legal_chunks")
    got = col.get(ids=["A_Dieu2"])
    assert got["documents"] == ["bị phạt"]
    assert got["metadatas"][0]["article"] == "Điều 2"
    assert "clause" not in got["metadatas"][0]


def test_rebuild_replaces_instead_of_duplicating(tmp_path):
    build_index(CHUNKS, fake_embed, tmp_path)
    build_index(CHUNKS[:1], fake_embed, tmp_path, rebuild=True)
    col = chromadb.PersistentClient(path=str(tmp_path)).get_collection("legal_chunks")
    assert col.count() == 1


def test_chunk_metadata_adds_numeric_validity_range():
    m = chunk_metadata({**CHUNKS[0], "expiry_date": "2021-01-01"})
    assert m["effective_from"] == 20200101
    assert m["effective_to"] == 20210101
    # CHUNKS không có khóa expiry_date -> còn hiệu lực
    assert chunk_metadata(CHUNKS[0])["effective_to"] == 99991231


def test_validity_range_filter_works_in_chroma(tmp_path):
    old = {**CHUNKS[0], "chunk_id": "OLD", "expiry_date": "2021-01-01"}
    col = build_index([old, CHUNKS[1]], fake_embed, tmp_path)

    def valid_at(d):
        where = {"$and": [{"effective_from": {"$lte": d}}, {"effective_to": {"$gt": d}}]}
        return sorted(col.get(where=where)["ids"])

    assert valid_at(20200301) == ["A_Dieu2", "OLD"]
    assert valid_at(20230101) == ["A_Dieu2"]


def test_fixed_chunk_without_articles_can_be_indexed(tmp_path):
    # Chroma từ chối list rỗng trong metadata
    c = {**CHUNKS[1], "chunk_id": "A_fixed0", "articles": []}
    assert build_index([c], fake_embed, tmp_path).count() == 1


def test_reindex_without_rebuild_clears_stale_fields(tmp_path):
    build_index([{**CHUNKS[0], "expiry_date": "2021-01-01"}], fake_embed, tmp_path)
    col = build_index([{**CHUNKS[0], "expiry_date": None}], fake_embed, tmp_path)
    meta = col.get(ids=["A_Dieu1_Khoan1"])["metadatas"][0]
    assert "expiry_date" not in meta
    assert meta["effective_to"] == 99991231


def test_variant_collection_and_plain_text(tmp_path):
    seen = []

    def recording_embed(texts):
        seen.extend(texts)
        return fake_embed(texts)

    build_index(CHUNKS, recording_embed, tmp_path, collection="legal_clause_plain", with_header=False)
    client = chromadb.PersistentClient(path=str(tmp_path))
    assert client.get_collection("legal_clause_plain").count() == 2
    assert seen == ["trả lãi", "bị phạt"]
    assert "legal_chunks" not in [c.name for c in client.list_collections()]


def test_rebuild_only_touches_its_own_collection(tmp_path):
    build_index(CHUNKS, fake_embed, tmp_path)
    build_index(CHUNKS[:1], fake_embed, tmp_path, rebuild=True, collection="legal_article")
    client = chromadb.PersistentClient(path=str(tmp_path))
    assert (client.get_collection("legal_chunks").count(), client.get_collection("legal_article").count()) == (2, 1)
