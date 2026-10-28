import pytest

from eval.metrics import article_ranking, drm_at, hit_at, mean, mrr_at, recall_at


def test_article_ranking_dedupes_clauses_and_uses_only_the_main_article_of_fixed_windows():
    chunks = [{"chunk_id": "X_Dieu1_Khoan1", "law_id": "X"}, {"chunk_id": "X_Dieu1_Khoan2", "law_id": "X"},
              {"chunk_id": "X_fixed0", "law_id": "X", "articles": ["Điều 5", "Điều 1", "Điều 6"], "main_article": "Điều 5"},
              {"chunk_id": "X_Dieu2", "law_id": "X"}, {"chunk_id": "X_fixed1", "law_id": "X", "articles": [], "main_article": None}]
    # cửa sổ cố định chỉ tính 1 hạng cho Điều chiếm nhiều từ nhất, không góp cả Điều phủ qua (làm tăng Hit@k ảo)
    assert article_ranking(chunks) == ["X_Dieu1", "X_Dieu5", "X_Dieu2"]


def test_ranking_metrics_by_hand():
    ranked, gold = ["a", "b", "c", "d"], ["c", "x"]
    assert (hit_at(ranked, gold, 2), hit_at(ranked, gold, 3)) == (0.0, 1.0)
    assert recall_at(ranked, gold, 4) == 0.5
    assert mrr_at(ranked, gold, 4) == pytest.approx(1 / 3)
    assert mrr_at(ranked, gold, 2) == 0.0


def test_drm_and_mean():
    chunks = [{"law_id": "X"}, {"law_id": "Y"}, {"law_id": "X"}, {"law_id": "Z"}]
    assert drm_at(chunks, ["X_Dieu1"], 4) == 0.5
    assert drm_at([], ["X_Dieu1"], 5) is None
    assert mean([1.0, None, 0.0]) == 0.5
    assert mean([None]) is None


from eval.metrics import citation_pr, refusal_correct, version_correct


@pytest.mark.parametrize("cited, gold, expected", [
    (["A", "B"], ["A"], (0.5, 1.0)),
    ([], ["A"], (None, 0.0)),
    (["A"], [], (0.0, None)),
    ([], [], (None, None)),
])
def test_citation_pr(cited, gold, expected):
    assert citation_pr(cited, gold) == expected


@pytest.mark.parametrize("kind, refused, ok", [
    ("out_of_scope", True, True), ("out_of_scope", False, False),
    ("situational", False, True), ("temporal", True, False),
])
def test_refusal_correct(kind, refused, ok):
    assert refusal_correct({"type": kind}, {"refused": refused}) is ok


def test_version_correct_only_for_temporal():
    case = {"type": "temporal", "gold_citations": ["BLLD2012_Dieu22_Khoan1"]}
    assert version_correct(case, ["BLLD2012"]) is True
    assert version_correct(case, ["BLLD2012", "BLLD2019"]) is False
    assert version_correct(case, []) is False
    assert version_correct({"type": "situational", "gold_citations": ["X_Dieu1"]}, ["X"]) is None
