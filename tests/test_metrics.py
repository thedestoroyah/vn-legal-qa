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
