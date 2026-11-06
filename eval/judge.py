"""Bộ chấm LLM (LLM-as-a-judge) cho Faithfulness và Answer Correctness: một lượt gọi mỗi câu trả lời (spec mục 7)."""
from src.generation.prompts import format_context
from src.ingestion.legal_chunker import ARTICLE_OUT_PATH, OUT_PATH, read_jsonl

SCORES = {0.0, 0.5, 1.0}
BAD_JSON = "bộ chấm không trả JSON hợp lệ"
JUDGE_ROLE = "Bạn là giám khảo chấm câu trả lời của một hệ thống hỏi đáp pháp luật Việt Nam."
JUDGE_RULES = """Chấm theo NỘI DUNG PHÁP LÝ: không trừ điểm vì diễn đạt khác, câu dài hơn, thêm chữ nối hay văn phong.

Tiêu chí 1 — faithfulness: mọi khẳng định trong câu trả lời có suy ra được từ các đoạn trích không (không so với đáp án mẫu).
- 1: mọi khẳng định đều có trong đoạn trích hoặc suy ra trực tiếp.
- 0.5: ý chính có căn cứ nhưng có chi tiết phụ không có trong đoạn trích.
- 0: ý chính không có trong đoạn trích hoặc mâu thuẫn với đoạn trích.
Câu gắn nhãn "(chưa có căn cứ)" vẫn là khẳng định cần kiểm.

Tiêu chí 2 — correctness: câu trả lời có khớp đáp án mẫu về kết luận, điều kiện, con số, thời hạn không.
- 1: khớp mọi ý chính của đáp án mẫu (thêm thông tin đúng không bị trừ).
- 0.5: đúng kết luận nhưng thiếu hoặc sai một điều kiện, con số, thời hạn.
- 0: sai kết luận hoặc không trả lời câu hỏi.
Không có đáp án mẫu thì correctness = null.

Chỉ trả về một đối tượng JSON: {"faithfulness": 0 | 0.5 | 1, "correctness": 0 | 0.5 | 1 | null, "reason": "<tối đa 2 câu>"}

Ví dụ 1:
Đoạn trích: [BLLD2019_Dieu35_Khoan1] ... b) Ít nhất 30 ngày nếu làm việc theo hợp đồng lao động xác định thời hạn có thời hạn từ 12 tháng đến 36 tháng;
Câu hỏi: Hợp đồng 24 tháng muốn nghỉ việc phải báo trước bao lâu?
Câu trả lời cần chấm: Phải báo trước cho người sử dụng lao động ít nhất 30 ngày [BLLD2019_Dieu35_Khoan1].
Đáp án mẫu: Báo trước ít nhất 30 ngày.
{"faithfulness": 1, "correctness": 1, "reason": "Đúng thời hạn 30 ngày, có trong đoạn trích; khác câu chữ không bị trừ."}

Ví dụ 2:
Đoạn trích: [BLDS2015_Dieu357_Khoan1] Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó phải trả lãi đối với số tiền chậm trả tương ứng với thời gian chậm trả.
Câu hỏi: Chậm trả tiền có phải trả lãi không, lãi suất tối đa bao nhiêu?
Câu trả lời cần chấm: Có, phải trả lãi, lãi suất tối đa 10%/năm [BLDS2015_Dieu357_Khoan1].
Đáp án mẫu: Có; lãi suất theo thỏa thuận nhưng không vượt quá 20%/năm (khoản 1 Điều 468).
{"faithfulness": 0.5, "correctness": 0.5, "reason": "Đúng là phải trả lãi nhưng mức 10% không có trong đoạn trích và sai so với 20%."}"""


def judge_messages(question, answer, contexts, reference):
    """Messages cho bộ chấm.

    Args:
        question: câu hỏi.
        answer: câu trả lời cần chấm.
        contexts: các chunk tác tử đã dùng làm ngữ cảnh.
        reference: đáp án mẫu; rỗng thì ghi rõ để bộ chấm trả correctness = null.
    """
    ref = f"Đáp án mẫu: {reference}" if reference else "Không có đáp án mẫu (correctness = null)."
    user = (f"Đoạn trích:\n{format_context(contexts)}\n\nCâu hỏi: {question}\n\n"
            f"Câu trả lời cần chấm:\n{answer}\n\n{ref}")
    return [{"role": "system", "content": f"{JUDGE_ROLE}\n\n{JUDGE_RULES}"}, {"role": "user", "content": user}]


def _score(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if value in SCORES else None


def judge(llm, case, response, contexts):
    """Chấm một câu trả lời; tự chấm bằng code các trường hợp từ chối và câu ngoài phạm vi (không tốn lượt gọi).

    Args:
        llm: LLM bộ chấm (from_env("JUDGE")).
        case: câu kiểm thử (type, question, reference_answer).
        response: phản hồi Phụ lục A.5 của tác tử.
        contexts: kết quả load_contexts(), để lấy nội dung các đoạn trong `retrieved_chunks`.

    Returns:
        {"faithfulness", "correctness", "reason", "called"}; điểm thuộc {0, 0.5, 1} hoặc None (không áp dụng / lỗi).
    """
    reference = (case.get("reference_answer") or "").strip()
    if response["refused"]:
        # câu trong phạm vi không có đáp án mẫu (Zalo): correctness không áp dụng; từ chối sai đã tính ở "Từ chối đúng"
        correctness = 1.0 if case["type"] == "out_of_scope" else (0.0 if reference else None)
        return {"faithfulness": None, "correctness": correctness, "reason": "từ chối", "called": False}
    if case["type"] == "out_of_scope":
        return {"faithfulness": None, "correctness": 0.0, "reason": "trả lời câu ngoài phạm vi", "called": False}
    used = used_contexts(response, contexts)
    try:
        out = llm.chat_json(judge_messages(case["question"], response["answer"], used, reference))
    except ValueError:
        return {"faithfulness": None, "correctness": None, "reason": BAD_JSON, "called": True}
    return {"faithfulness": _score(out.get("faithfulness")),
            "correctness": _score(out.get("correctness")) if reference else None,
            "reason": str(out.get("reason") or "")[:300], "called": True}


def load_contexts():
    """Nội dung chunk để dựng lại ngữ cảnh tác tử đã thấy: {"clause": {id: chunk Khoản}, "article": {id: chunk Điều}}.

    Hai dict tách riêng vì phần dẫn nhập của Điều trùng chunk_id với chunk Điều (140 Điều): tác tử chỉ thấy
    bản Điều đầy đủ khi đi nhánh lookup_article.
    """
    return {"clause": {c["chunk_id"]: c for c in read_jsonl(OUT_PATH)},
            "article": {c["chunk_id"]: c for c in read_jsonl(ARTICLE_OUT_PATH)}}


def used_contexts(response, contexts):
    """Các chunk tác tử thực sự dùng làm ngữ cảnh, theo thứ tự `retrieved_chunks`.

    Args:
        response: phản hồi Phụ lục A.5 (cần retrieved_chunks và trace).
        contexts: kết quả load_contexts().

    Returns:
        list chunk; đoạn lấy qua lookup_article dùng bản Điều, đoạn truy xuất dùng bản Khoản (hoặc Điều nếu không có).
    """
    looked = {cid for s in response["trace"] if s["node"] == "lookup_article" for cid in s["output"].get("evidence", [])}
    used = []
    for item in response["retrieved_chunks"]:
        cid = item["chunk_id"]
        found = contexts["article"].get(cid) if cid in looked else (contexts["clause"].get(cid) or contexts["article"].get(cid))
        if found:
            used.append(found)
    return used
