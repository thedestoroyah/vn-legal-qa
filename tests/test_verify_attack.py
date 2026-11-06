import random
from types import SimpleNamespace

from eval import verify_attack as va
from tests.agent_fakes import chunk, make_llm

ANSWER = "Câu một [BLDS2015_Dieu357_Khoan1]. Câu hai [BLDS2015_Dieu468_Khoan1] [BLDS2015_Dieu357_Khoan1]."


def test_inject_replaces_code_only_in_target_sentence():
    out = va.inject(ANSWER, 2, "BLDS2015_Dieu357_Khoan1", "BLLD2019_Dieu35_Khoan1")
    assert out == "Câu một [BLDS2015_Dieu357_Khoan1]. Câu hai [BLDS2015_Dieu468_Khoan1] [BLLD2019_Dieu35_Khoan1]."


def test_same_context_distractor_skips_cited_gold_and_same_article():
    used = [chunk(c) for c in ("BLDS2015_Dieu357_Khoan1", "BLDS2015_Dieu357_Khoan2", "BLDS2015_Dieu468_Khoan1",
                               "BLDS2015_Dieu300_Khoan1", "BLDS2015_Dieu400_Khoan1")]
    gold = {"BLDS2015_Dieu400"}
    picked = va.same_context_distractor(ANSWER, "BLDS2015_Dieu357_Khoan1", used, gold, random.Random(0))
    assert picked["chunk_id"] == "BLDS2015_Dieu300_Khoan1"
    assert va.same_context_distractor(ANSWER, "BLDS2015_Dieu357_Khoan1", used[:3], gold, random.Random(0)) is None


def test_other_law_distractor_comes_from_a_law_not_cited():
    pool = [chunk("BLDS2015_Dieu1_Khoan1"), chunk("BLLD2019_Dieu35_Khoan1")]
    picked = va.other_law_distractor(ANSWER, pool, random.Random(0))
    assert picked["law_id"] == "BLLD2019"


def test_attack_counts_detection_and_false_alarms(tmp_path):
    used = [chunk("BLDS2015_Dieu357_Khoan1"), chunk("BLDS2015_Dieu468_Khoan1")]
    bad = chunk("BLLD2019_Dieu35_Khoan1")
    llm = make_llm(tmp_path, verify=[{"unsupported": [{"sentence": 2, "chunk_id": "BLLD2019_Dieu35_Khoan1"},
                                                      {"sentence": 1, "chunk_id": "BLDS2015_Dieu357_Khoan1"}]}])
    row = va.attack(llm, ANSWER, used, 2, "BLDS2015_Dieu357_Khoan1", bad)
    assert row == {"detected": True, "false_alarms": 1, "other_pairs": 2}


def test_attack_counts_missed_when_llm_flags_nothing(tmp_path):
    used = [chunk("BLDS2015_Dieu357_Khoan1"), chunk("BLDS2015_Dieu468_Khoan1")]
    llm = make_llm(tmp_path, verify=[{"unsupported": []}])
    row = va.attack(llm, ANSWER, used, 0, "BLDS2015_Dieu357_Khoan1", chunk("BLLD2019_Dieu35_Khoan1"))
    assert row == {"detected": False, "false_alarms": 0, "other_pairs": 2}


def test_summary_rates_per_kind():
    rows = [{"kind": "same_context", "detected": True, "false_alarms": 0, "other_pairs": 2},
            {"kind": "same_context", "detected": False, "false_alarms": 1, "other_pairs": 2},
            {"kind": "other_law", "detected": True, "false_alarms": 0, "other_pairs": 0}]
    assert va.summary(rows) == {"same_context": (2, 0.5, 0.25), "other_law": (1, 1.0, None)}


def test_other_law_distractor_treats_old_and_new_labour_code_as_one_family():
    pool = [chunk("BLLD2012_Dieu37_Khoan1"), chunk("BLDS2015_Dieu1_Khoan1")]
    picked = va.other_law_distractor("Câu [BLLD2019_Dieu35_Khoan1].", pool, random.Random(0))
    assert picked["law_id"] == "BLDS2015"


def test_inject_handles_grouped_codes_and_does_not_touch_longer_ids():
    text = "Câu [BLLD2019_Dieu17_Khoan1, BLLD2019_Dieu17_Khoan10]."
    assert va.inject(text, 0, "BLLD2019_Dieu17_Khoan1", "X_Dieu1") == "Câu [X_Dieu1, BLLD2019_Dieu17_Khoan10]."


def test_inject_raises_when_code_not_in_sentence():
    import pytest
    with pytest.raises(ValueError):
        va.inject(ANSWER, 0, "BLDS2015_Dieu468_Khoan1", "X_Dieu1")


def test_cmd_run_repairs_cut_off_line_before_appending(tmp_path, monkeypatch):
    path = tmp_path / "v.jsonl"
    path.write_text('{"id": "A", "kind": "x"}\n{"id": ', encoding="utf-8")
    monkeypatch.setattr(va, "OUT_PATH", path)
    monkeypatch.setattr("src.generation.llm.from_env", lambda prefix: SimpleNamespace(calls=0))
    monkeypatch.setattr(va, "load_contexts", lambda: {"clause": {}})
    monkeypatch.setattr(va, "_targets", lambda n: [])
    va.cmd_run(SimpleNamespace(n=1))
    assert path.read_text(encoding="utf-8") == '{"id": "A", "kind": "x"}\n'
