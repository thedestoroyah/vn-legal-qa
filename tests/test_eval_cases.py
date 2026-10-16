import pytest

from eval.cases import validate_cases
from eval.import_cases import load_manual, read_exclude, synthetic_cases, zalo_cases
from eval.show_article import format_article

LAWS = {"BLDS2015": {"number": "91/2015/QH13", "domain": "dan_su"},
        "LDN2020": {"number": "59/2020/QH14", "domain": "doanh_nghiep"}}
CHUNK_IDS = ["BLDS2015_Dieu321_Khoan1", "BLDS2015_Dieu321_Khoan2", "BLDS2015_Dieu630", "LDN2020_Dieu47_Khoan1"]


def case(**over):
    base = {"id": "M_001", "question": "Câu hỏi?", "type": "situational", "domain": "dan_su", "event_date": None,
            "gold_citations": ["BLDS2015_Dieu321_Khoan1"], "reference_answer": "", "source": "manual",
            "checked_by": None}
    return {**base, **over}


def test_valid_cases_have_no_errors():
    cases = [case(), case(id="M_002", gold_citations=["BLDS2015_Dieu321"]),
             case(id="M_003", type="temporal", event_date="2020-03-01"),
             case(id="M_004", type="out_of_scope", domain="ngoai_pham_vi", gold_citations=[])]
    assert validate_cases(cases, CHUNK_IDS) == []


@pytest.mark.parametrize("over, msg", [
    ({"type": "lookup"}, "type"),
    ({"domain": "hinh_su"}, "domain"),
    ({"source": "vlqa"}, "source"),
    ({"question": "  "}, "question rỗng"),
    ({"event_date": "2020"}, "event_date"),
    ({"type": "temporal"}, "temporal phải có event_date"),
    ({"type": "out_of_scope", "domain": "ngoai_pham_vi"}, "out_of_scope"),
    ({"gold_citations": []}, "thiếu gold_citations"),
    ({"gold_citations": "BLDS2015_Dieu321"}, "danh sách"),
    ({"gold_citations": ["BLDS2015_Dieu321_Khoan9"]}, "BLDS2015_Dieu321_Khoan9"),
    ({"gold_citations": ["BLDS2015_Dieu999"]}, "BLDS2015_Dieu999"),
])
def test_invalid_case_reports_one_reason(over, msg):
    errors = validate_cases([case(**over)], CHUNK_IDS)
    assert len(errors) == 1 and errors[0].startswith("M_001:") and msg in errors[0]


def test_missing_field_and_duplicate_id():
    bad = {k: v for k, v in case().items() if k != "checked_by"}
    assert validate_cases([case(), case(), bad], CHUNK_IDS) == ["M_001: id trùng", "M_001: thiếu trường checked_by"]


def test_zalo_keeps_only_questions_fully_inside_corpus():
    queries = {"aaaaaaaa11": " Thuê ô tô đang thế chấp? ", "bbbbbbbb22": "Phạt không mang bằng lái?",
               "cccccccc33": "Hai luật?"}
    qrels = [("aaaaaaaa11", "91/2015/qh13+321"), ("bbbbbbbb22", "100/2019/nđ-cp+21"),
             ("cccccccc33", "91/2015/qh13+630"), ("cccccccc33", "59/2020/qh14+47"), ("dddddddd44", "91/2015/qh13+1")]
    cases = zalo_cases(queries, qrels, LAWS)
    assert [c["id"] for c in cases] == ["Z_aaaaaaaa", "Z_cccccccc"]
    assert (cases[0]["question"], cases[0]["gold_citations"], cases[0]["domain"], cases[0]["source"]) == (
        "Thuê ô tô đang thế chấp?", ["BLDS2015_Dieu321"], "dan_su", "zalo")
    assert cases[1]["gold_citations"] == ["BLDS2015_Dieu630", "LDN2020_Dieu47"]
    assert validate_cases(cases, CHUNK_IDS) == []


def test_zalo_exclude_file_with_comments(tmp_path):
    path = tmp_path / "ex.txt"
    path.write_text("Z_aaaaaaaa  # căn cứ đã bị sửa\n\n# ghi chú\n", encoding="utf-8")
    exclude = read_exclude(path)
    assert exclude == {"Z_aaaaaaaa"}
    assert zalo_cases({"aaaaaaaa11": "q"}, [("aaaaaaaa11", "91/2015/qh13+321")], LAWS, exclude) == []
    assert read_exclude(tmp_path / "missing.txt") == frozenset()


def test_synthetic_maps_clauses_and_uncovered_articles():
    raw = [{"id": "DS_001", "law_number": "91/2015/QH13", "question": " Hỏi? ", "expected_answer": "Đáp.",
            "ground_truth": {"articles": ["321", "630"], "clauses": ["321.2"]}}]
    [c] = synthetic_cases(raw, LAWS)
    assert c["gold_citations"] == ["BLDS2015_Dieu321_Khoan2", "BLDS2015_Dieu630"]
    assert (c["question"], c["reference_answer"], c["source"], c["type"]) == ("Hỏi?", "Đáp.", "synthetic", "situational")


def test_synthetic_unknown_law_fails_loudly():
    raw = [{"id": "TM_009", "law_number": "1/2000/QH10", "question": "q", "ground_truth": {"articles": ["1"], "clauses": []}}]
    with pytest.raises(ValueError, match="TM_009"):
        synthetic_cases(raw, LAWS)


def test_load_manual_missing_and_broken(tmp_path):
    assert load_manual(tmp_path / "none.json") == []
    broken = tmp_path / "manual.json"
    broken.write_text('[{"id": "M_001",}]', encoding="utf-8")
    with pytest.raises(SystemExit, match="không phải JSON hợp lệ"):
        load_manual(broken)


def test_format_article_lists_chunk_ids_in_order():
    chunks = [{"chunk_id": "BLDS2015_Dieu321_Khoan1", "article": "Điều 321", "article_title": "Quyền của bên thế chấp", "content": "A"},
              {"chunk_id": "BLDS2015_Dieu3210_Khoan1", "article": "Điều 3210", "article_title": "X", "content": "Z"},
              {"chunk_id": "BLDS2015_Dieu321_Khoan2", "article": "Điều 321", "article_title": "Quyền của bên thế chấp", "content": "B"}]
    assert format_article(chunks, "BLDS2015", "321") == (
        "BLDS2015 Điều 321. Quyền của bên thế chấp\n[BLDS2015_Dieu321_Khoan1] A\n[BLDS2015_Dieu321_Khoan2] B")
    assert format_article(chunks, "BLDS2015", "999") == "Không tìm thấy BLDS2015 Điều 999"
