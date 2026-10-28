import csv

import pytest

from eval import agent_eval
from eval.judge import JUDGE_ROLE, judge, judge_messages
from src.generation.llm import LLM
from tests.agent_fakes import ScriptedClient, chunk

A = "BLDS2015_Dieu357_Khoan1"
CTX = {"clause": {A: chunk(A, "Bên chậm trả tiền phải trả lãi.")}, "article": {}}


class JudgeClient(ScriptedClient):
    """Client giả cho bộ chấm: prompt chấm không có câu vai trò của tác tử nên lấy trả lời theo khóa 'judge'."""

    def _create(self, model, messages, **params):
        assert messages[0]["content"].startswith(JUDGE_ROLE)
        self.seen.append(("judge", messages))
        return self._wrap(self.replies["judge"].pop(0))


def judge_llm(tmp_path, *replies):
    return LLM(JudgeClient(judge=list(replies)), "judge", tmp_path)


def case(kind="situational", reference="Phải trả lãi."):
    return {"id": "q1", "type": kind, "question": "Chậm trả có phải trả lãi?", "gold_citations": [A],
            "reference_answer": reference, "source": "manual"}


def resp(refused=False):
    return {"answer": f"Có, phải trả lãi [{A}].", "refused": refused, "citations": [{"chunk_id": A}],
            "retrieved_chunks": [{"chunk_id": A, "score": 1.0}], "trace": []}


@pytest.mark.parametrize("kind, refused, correctness", [
    ("out_of_scope", True, 1.0), ("situational", True, 0.0), ("out_of_scope", False, 0.0),
])
def test_rule_based_cases_do_not_call_llm(tmp_path, kind, refused, correctness):
    llm = judge_llm(tmp_path)
    out = judge(llm, case(kind), resp(refused), CTX)
    assert (out["faithfulness"], out["correctness"], out["called"]) == (None, correctness, False)
    assert llm.calls == 0


def test_judge_parses_and_snaps_scores(tmp_path):
    llm = judge_llm(tmp_path, {"faithfulness": 1, "correctness": "0.5", "reason": "thiếu ý"})
    assert judge(llm, case(), resp(), CTX) == {"faithfulness": 1.0, "correctness": 0.5, "reason": "thiếu ý",
                                                "called": True}


def test_judge_invalid_score_becomes_none(tmp_path):
    llm = judge_llm(tmp_path, {"faithfulness": 0.7, "correctness": "cao", "reason": ""})
    out = judge(llm, case(), resp(), CTX)
    assert (out["faithfulness"], out["correctness"]) == (None, None)


def test_judge_without_reference_has_null_correctness(tmp_path):
    llm = judge_llm(tmp_path, {"faithfulness": 1, "correctness": 1, "reason": ""})
    out = judge(llm, case(reference=""), resp(), CTX)
    assert (out["faithfulness"], out["correctness"]) == (1.0, None)
    assert "Không có đáp án mẫu" in llm.client.seen[0][1][-1]["content"]


def test_judge_bad_json_gives_none(tmp_path):
    out = judge(judge_llm(tmp_path, "không", "vẫn không"), case(), resp(), CTX)
    assert (out["faithfulness"], out["correctness"], out["called"]) == (None, None, True)


def test_judge_messages_contain_contexts_answer_and_reference():
    user = judge_messages("Q?", "Trả lời [X].", [CTX["clause"][A]], "Đáp án.")[-1]["content"]
    assert "Câu hỏi: Q?" in user and "Bên chậm trả tiền phải trả lãi." in user
    assert "Câu trả lời cần chấm:\nTrả lời [X]." in user and "Đáp án mẫu: Đáp án." in user


def test_judge_results_resume(tmp_path):
    out = tmp_path / "j.jsonl"
    results = {("q1", "full"): resp()}
    llm = judge_llm(tmp_path, {"faithfulness": 1, "correctness": 1, "reason": ""})
    assert agent_eval.judge_results(llm, [case()], results, out, CTX) == 1
    assert agent_eval.judge_results(judge_llm(tmp_path), [case()], results, out, CTX) == 0


def test_write_sheet_has_blank_score_columns_and_no_llm_scores(tmp_path):
    path = tmp_path / "s.csv"
    results = {("q1", "full"): resp(), ("q2", "full"): resp(refused=True)}
    cases = [case(), {**case(), "id": "q2"}]
    assert agent_eval.write_sheet(cases, results, "full", 5, path, CTX) == 1  # câu từ chối không cần chấm tay
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    assert rows[0]["id"] == "q1" and rows[0]["faithfulness"] == "" and "Bên chậm trả tiền" in rows[0]["contexts"]


def test_agreement_reads_vietnamese_decimal_and_skips_blank():
    sheet = [{"id": "a", "faithfulness": "1", "correctness": "0,5"},
             {"id": "b", "faithfulness": "0", "correctness": " "},
             {"id": "c", "faithfulness": "1", "correctness": "1"}]
    judged = {("a", "full"): {"faithfulness": 1.0, "correctness": 0.5},
              ("b", "full"): {"faithfulness": 1.0, "correctness": 1.0},
              ("c", "full"): {"faithfulness": None, "correctness": 1.0}}
    assert agent_eval.agreement(sheet, judged, "full") == {"faithfulness": (0.5, 2), "correctness": (1.0, 2)}


def test_refusal_without_reference_has_null_correctness(tmp_path):
    # câu Zalo không có đáp án mẫu: điểm 0 cho lượt từ chối sẽ làm trung bình correctness chỉ tính trên các lượt từ chối
    out = judge(judge_llm(tmp_path), case(reference=""), resp(refused=True), CTX)
    assert (out["faithfulness"], out["correctness"], out["called"]) == (None, None, False)


def test_used_contexts_prefers_clause_chunk_unless_article_was_looked_up():
    from eval.agent_eval import used_contexts
    pre = "BLDS2015_Dieu5"
    contexts = {"clause": {pre: chunk(pre, "dẫn nhập")}, "article": {pre: chunk(pre, "dẫn nhập\n1. khoản một")}}
    retrieved = {"retrieved_chunks": [{"chunk_id": pre}], "trace": [{"node": "retrieve", "output": {"evidence": [pre]}}]}
    looked = {"retrieved_chunks": [{"chunk_id": pre}], "trace": [{"node": "lookup_article", "output": {"evidence": [pre]}}]}
    assert [c["content"] for c in used_contexts(retrieved, contexts)] == ["dẫn nhập"]
    assert [c["content"] for c in used_contexts(looked, contexts)] == ["dẫn nhập\n1. khoản một"]
