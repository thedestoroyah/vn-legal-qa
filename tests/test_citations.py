from src.generation.citations import (NO_BASIS, cited_ids, cited_sentences, drop_citations, drop_pairs,
                                      label_sentences, lost_sentences, sentences, strip_unknown)

A, B, C = "BLDS2015_Dieu357_Khoan1", "BLDS2015_Dieu357_Khoan2", "BLLD2019_Dieu35"


def test_cited_ids_reads_single_and_grouped_brackets_in_order():
    assert cited_ids(f"Câu một [{A}]. Câu hai [{B}, {C}; {A}].") == [A, B, C]


def test_non_citation_brackets_are_ignored():
    assert cited_ids("Xem [1] và [ghi chú] [Điều 5].") == []


def test_sentences_round_trip_and_split_on_end_punct_and_newlines():
    text = f"Có [{A}]. Lãi do thỏa thuận [{B}]!\n- Ý phụ"
    parts = sentences(text)
    assert "".join(parts) == text
    assert parts[0::2] == [f"Có [{A}].", f"Lãi do thỏa thuận [{B}]!", "- Ý phụ"]


def test_drop_citations_removes_only_listed_ids_and_empty_brackets():
    assert drop_citations(f"X [{A}, {B}]. Y [{C}]. Z [1].", {B, C}) == f"X [{A}]. Y. Z [1]."


def test_strip_unknown_removes_ids_outside_context():
    text, removed = strip_unknown(f"X [{A}, BLDS2015_Dieu999]. Y [BLDS2015_Dieu1000].", {A})
    assert text == f"X [{A}]. Y."
    assert removed == ["BLDS2015_Dieu999", "BLDS2015_Dieu1000"]


def test_strip_unknown_accepts_dict_of_evidence():
    assert strip_unknown(f"X [{A}].", {A: {"chunk_id": A}}) == (f"X [{A}].", [])


def test_cited_sentences_lists_only_sentences_with_ids():
    text = f"Mở đầu. Có [{A}]. Không. Hai mã [{B}, {C}]."
    assert cited_sentences(text) == [(2, f"Có [{A}].", [A]), (6, f"Hai mã [{B}, {C}].", [B, C])]


def test_drop_pairs_only_touches_given_sentence():
    assert drop_pairs(f"Một [{A}]. Hai [{A}, {B}].", {2: {A}}) == f"Một [{A}]. Hai [{B}]."


def test_lost_sentences_finds_sentences_that_had_ids_and_lost_all():
    assert lost_sentences(f"A1 [{A}]. A2 [{A}, {B}]. A3.", f"A1. A2 [{B}]. A3.") == [0]


def test_label_sentences_appends_marker_before_final_punct():
    assert label_sentences("Một. Hai.", [2]) == f"Một. Hai {NO_BASIS}."
    assert label_sentences("Không dấu", [0]) == f"Không dấu {NO_BASIS}"


def test_normalize_ids_maps_clause_id_to_article_chunk_in_context():
    from src.generation.citations import normalize_ids
    text = f"Có [BLLD2019_Dieu35_Khoan1]. Khác [{A}]. Lạ [BLDS2015_Dieu999_Khoan2]."
    assert normalize_ids(text, {"BLLD2019_Dieu35", A}) == f"Có [BLLD2019_Dieu35]. Khác [{A}]. Lạ [BLDS2015_Dieu999_Khoan2]."
