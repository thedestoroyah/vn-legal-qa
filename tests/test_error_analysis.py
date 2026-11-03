import pytest

from eval import error_analysis
from eval.error_analysis import count_categories, hints, parse_categories, pick


def test_hints_order_and_none_skipped():
    row = {"answered": 1.0, "refusal_ok": 1.0, "version_ok": 0.0, "recall": 0.5, "precision": None, "correctness": 1.0}
    assert hints(row) == ["sai_phien_ban", "thieu_can_cu"]
    assert hints({"answered": 0.0, "refusal_ok": 0.0, "version_ok": None, "recall": 0.0,
                  "precision": None, "correctness": None}) == ["tu_choi_nham", "thieu_can_cu"]
    assert hints({"answered": 1.0, "refusal_ok": 1.0, "version_ok": None, "recall": 1.0,
                  "precision": 1.0, "correctness": 1.0}) == []


def test_pick_is_deterministic_and_covers_groups():
    rows = [{"id": f"r{i}", "answered": 0.0, "refusal_ok": 0.0, "recall": 0.0} for i in range(10)]
    rows += [{"id": f"v{i}", "answered": 1.0, "refusal_ok": 1.0, "version_ok": 0.0} for i in range(10)]
    first = [r["id"] for r in pick(rows, 4)]
    assert first == [r["id"] for r in pick(rows, 4)]
    assert {i[0] for i in first} == {"r", "v"}


def test_parse_categories_normalizes_and_rejects_unknown():
    assert parse_categories(" Sai_Phien_Ban ; dinh_tuyen_sai") == ["sai_phien_ban", "dinh_tuyen_sai"]
    for bad in ("", " ; ", "loi_la"):
        with pytest.raises(ValueError):
            parse_categories(bad)


def test_count_categories_names_bad_row():
    with pytest.raises(ValueError, match="M_001"):
        count_categories([{"id": "M_001", "category": ""}])
    assert count_categories([{"id": "A", "category": "sai_van_ban;khac"}, {"id": "B", "category": "khac"}])["khac"] == 2


def test_sheet_refuses_to_overwrite_filled_sheet(tmp_path, monkeypatch):
    out = tmp_path / "errors.csv"
    out.write_text("id,category\nA,khac\n", encoding="utf-8")
    monkeypatch.setattr(error_analysis, "SHEET_PATH", out)
    with pytest.raises(SystemExit):
        error_analysis.main(["sheet"])
    assert "A,khac" in out.read_text(encoding="utf-8")


def test_sheet_writes_bom_so_excel_reads_vietnamese(tmp_path, monkeypatch):
    out = tmp_path / "errors.csv"
    monkeypatch.setattr(error_analysis, "SHEET_PATH", out)
    error_analysis.main(["sheet", "--n", "2"])
    assert out.read_bytes().startswith(b"\xef\xbb\xbf")


def test_categories_include_metric_artifacts_and_incomplete_answers():
    labels = "trich_them_lien_quan; bo_cham_qua_chat; tra_loi_thieu_y; khong_phai_loi"
    assert parse_categories(labels) == ["trich_them_lien_quan", "bo_cham_qua_chat", "tra_loi_thieu_y", "khong_phai_loi"]
