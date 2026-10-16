from src.retrieval.bm25 import BM25Index, tokenize


def chunk(cid, content, eff="2017-01-01", expiry=None):
    return {"chunk_id": cid, "content": content, "effective_date": eff, "expiry_date": expiry}


CHUNKS = [
    chunk("A", "Bên có nghĩa vụ chậm trả tiền thì phải trả lãi đối với số tiền chậm trả."),
    chunk("B", "Người lao động có quyền đơn phương chấm dứt hợp đồng lao động.", eff="2021-01-01"),
    chunk("C", "Doanh nghiệp tư nhân do một cá nhân làm chủ."),
    chunk("D", "Hợp đồng lao động theo mùa vụ dưới 12 tháng.", eff="2013-05-01", expiry="2021-01-01"),
]


def test_tokenize_joins_compound_words_lowercases_and_drops_punctuation():
    tokens = tokenize("Người lao động chấm dứt hợp đồng, được không?")
    assert {"lao_động", "chấm_dứt", "hợp_đồng"} <= set(tokens)
    assert all(t == t.lower() and t.replace("_", "").isalnum() for t in tokens)


def test_search_ranks_matching_chunk_first():
    hits = BM25Index(CHUNKS).search("chậm trả tiền phải trả lãi", k=5)
    assert hits[0][0] == "A"
    assert hits == sorted(hits, key=lambda h: -h[1])


def test_search_respects_validity_date():
    index = BM25Index(CHUNKS)
    assert "D" not in [cid for cid, _ in index.search("hợp đồng lao động mùa vụ")]
    assert [cid for cid, _ in index.search("hợp đồng lao động mùa vụ", date="2020-03-01")] == ["D"]


def test_search_with_text_fn_and_empty_query():
    index = BM25Index(CHUNKS, text_fn=lambda c: f"Bộ luật Dân sự {c['content']}")
    assert index.search("?!") == []
    assert index.search("chậm trả", k=1)[0][0] == "A"
