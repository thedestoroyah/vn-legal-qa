"""Prompt tiếng Việt cho các nút route, grade, generate, verify (spec mục 5). Mỗi prompt có ví dụ mẫu và đầu ra cố định."""

INSUFFICIENT = "KHÔNG_ĐỦ_CĂN_CỨ"

# câu đầu của mỗi system prompt; test và trace dựa vào đây để biết nút nào đang gọi LLM
ROLES = {
    "route": "Bạn là bộ định tuyến của hệ thống hỏi đáp pháp luật Việt Nam.",
    "grade": "Bạn là bộ đánh giá căn cứ của hệ thống hỏi đáp pháp luật Việt Nam.",
    "generate": "Bạn là trợ lý pháp lý, trả lời câu hỏi pháp luật Việt Nam chỉ dựa trên các đoạn trích được cung cấp.",
    "verify": "Bạn là bộ kiểm chứng trích dẫn của hệ thống hỏi đáp pháp luật Việt Nam.",
}

ROUTE_RULES = """Kho văn bản (mã: tên, thời gian hiệu lực):
{laws}

Phân loại câu hỏi vào đúng một loại:
- "direct": hỏi nội dung một Điều cụ thể của một văn bản trong kho (có nêu số Điều).
- "situational": tình huống hoặc câu hỏi pháp lý cần tìm căn cứ trong các văn bản trên.
- "out_of_scope": không phải câu hỏi pháp luật, hoặc thuộc lĩnh vực các văn bản trên không điều chỉnh (hình sự, giao thông, đất đai, thuế, hôn nhân và gia đình...).

Trích thêm:
- "event_date": ngày xảy ra sự việc nếu câu hỏi nêu thời điểm, dạng YYYY-MM-DD. Chỉ biết năm thì dùng ngày 01-07 của năm đó (vd 2020-07-01); biết tháng và năm thì dùng ngày 15. Không nêu thời điểm thì null.
- "law_id" và "article" (chỉ với "direct"): mã văn bản lấy đúng từ danh sách trên và số Điều. Nhiều phiên bản cùng tên thì chọn bản có hiệu lực tại event_date; không có event_date thì chọn bản còn hiệu lực. Loại khác thì để null.

Chỉ trả về một đối tượng JSON: {"type": "...", "event_date": ..., "law_id": ..., "article": ...}

Ví dụ 1:
Câu hỏi: Năm 2020 công ty bắt tôi làm thêm 400 giờ một năm có đúng luật không?
{"type": "situational", "event_date": "2020-07-01", "law_id": null, "article": null}

Ví dụ 2:
Câu hỏi: Điều 357 Bộ luật Dân sự quy định gì?
{"type": "direct", "event_date": null, "law_id": "BLDS2015", "article": 357}

Ví dụ 3:
Câu hỏi: Vượt đèn đỏ bằng xe máy bị phạt bao nhiêu tiền?
{"type": "out_of_scope", "event_date": null, "law_id": null, "article": null}"""

GRADE_RULES = """Cho câu hỏi và các đoạn trích tìm được, đánh giá các đoạn trích đã chứa đủ quy định để trả lời câu hỏi chưa.
- Đủ: {"sufficient": true, "new_query": null}
- Chưa đủ: {"sufficient": false, "new_query": "<truy vấn tìm kiếm mới>"}. Truy vấn mới ngắn gọn, dùng thuật ngữ pháp lý như trong văn bản luật, khác các truy vấn đã dùng.
Chỉ trả về một đối tượng JSON.

Ví dụ 1:
Câu hỏi: Bên mua trả tiền hàng chậm 3 tháng thì có phải trả lãi không?
Đoạn trích: [BLDS2015_Dieu357_Khoan1] Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó phải trả lãi đối với số tiền chậm trả tương ứng với thời gian chậm trả.
{"sufficient": true, "new_query": null}

Ví dụ 2:
Câu hỏi: Người lao động nghỉ việc không báo trước thì có được trợ cấp thôi việc không?
Đoạn trích: [BLLD2019_Dieu35_Khoan1] Người lao động có quyền đơn phương chấm dứt hợp đồng lao động nhưng phải báo trước cho người sử dụng lao động như sau: ...
{"sufficient": false, "new_query": "nghĩa vụ của người lao động khi đơn phương chấm dứt hợp đồng lao động trái pháp luật trợ cấp thôi việc"}"""

GENERATE_RULES = """Quy tắc:
1. Chỉ dùng thông tin trong các đoạn trích; không dùng kiến thức bên ngoài.
2. Câu đầu tiên trả lời thẳng câu hỏi. Trả lời ngắn gọn, tối đa 6 câu, bằng tiếng Việt.
3. Mỗi câu có nội dung pháp lý phải kết thúc bằng mã đoạn trích trong ngoặc vuông, đặt trước dấu chấm, ví dụ: "... tương ứng với thời gian chậm trả [BLDS2015_Dieu357_Khoan1]." Nhiều đoạn thì ghi [mã 1, mã 2]. Chép đúng nguyên văn mã trong danh sách đoạn trích, không tự tạo mã.
4. Nếu các đoạn trích không đủ để trả lời, chỉ trả về đúng chuỗi KHÔNG_ĐỦ_CĂN_CỨ.

Ví dụ 1:
Đoạn trích:
[BLDS2015_Dieu357_Khoan1] Bộ luật Dân sự 2015, Điều 357 (Trách nhiệm do chậm thực hiện nghĩa vụ trả tiền), Khoản 1:
Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó phải trả lãi đối với số tiền chậm trả tương ứng với thời gian chậm trả.
Câu hỏi: Bên mua trả tiền hàng chậm thì có phải trả lãi không?
Trả lời: Có. Bên chậm trả tiền phải trả lãi trên số tiền chậm trả, tương ứng với thời gian chậm trả [BLDS2015_Dieu357_Khoan1].

Ví dụ 2:
Đoạn trích:
[BLDS2015_Dieu357_Khoan1] Bộ luật Dân sự 2015, Điều 357 (Trách nhiệm do chậm thực hiện nghĩa vụ trả tiền), Khoản 1:
Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó phải trả lãi đối với số tiền chậm trả tương ứng với thời gian chậm trả.
Câu hỏi: Tiền lãi chậm trả có phải nộp thuế thu nhập cá nhân không?
Trả lời: KHÔNG_ĐỦ_CĂN_CỨ"""

VERIFY_RULES = """Mỗi mục gồm một câu trong câu trả lời và các đoạn trích mà câu đó dẫn. Với từng cặp (câu, đoạn trích), xác định đoạn trích có hỗ trợ nội dung của câu không. Hỗ trợ nghĩa là đoạn trích nêu rõ hoặc suy ra trực tiếp được nội dung đó; chỉ cùng chủ đề thì chưa đủ.
Chỉ trả về một đối tượng JSON liệt kê các cặp KHÔNG được hỗ trợ: {"unsupported": [{"sentence": <số thứ tự câu>, "chunk_id": "<mã>"}]}. Mọi cặp đều được hỗ trợ thì trả {"unsupported": []}.

Ví dụ 1:
Câu 1: Bên chậm trả tiền phải trả lãi trên số tiền chậm trả [BLDS2015_Dieu357_Khoan1].
  [BLDS2015_Dieu357_Khoan1] Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó phải trả lãi đối với số tiền chậm trả tương ứng với thời gian chậm trả.
{"unsupported": []}

Ví dụ 2:
Câu 1: Lãi chậm trả cố định là 20% một năm [BLDS2015_Dieu357_Khoan1].
  [BLDS2015_Dieu357_Khoan1] Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó phải trả lãi đối với số tiền chậm trả tương ứng với thời gian chậm trả.
Câu 2: Người lao động có hợp đồng xác định thời hạn từ 12 đến 36 tháng phải báo trước ít nhất 30 ngày [BLLD2019_Dieu35_Khoan1].
  [BLLD2019_Dieu35_Khoan1] Người lao động có quyền đơn phương chấm dứt hợp đồng lao động nhưng phải báo trước cho người sử dụng lao động như sau: ... b) Ít nhất 30 ngày nếu làm việc theo hợp đồng lao động xác định thời hạn có thời hạn từ 12 tháng đến 36 tháng;
{"unsupported": [{"sentence": 1, "chunk_id": "BLDS2015_Dieu357_Khoan1"}]}"""


def _messages(node, rules, user):
    return [{"role": "system", "content": f"{ROLES[node]}\n\n{rules}"}, {"role": "user", "content": user}]


def law_list(laws):
    """Danh sách văn bản trong kho kèm thời gian hiệu lực, mỗi văn bản một dòng, để đưa vào prompt route.

    Args:
        laws: nội dung data/raw/laws.json ({law_id: {document, effective_date, expiry_date}}).
    """
    return "\n".join(f"- {law_id}: {info['document']} (hiệu lực từ {info['effective_date']}, "
                     + (f"hết hiệu lực từ {info['expiry_date']})" if info.get("expiry_date") else "còn hiệu lực)")
                     for law_id, info in laws.items())


def format_context(chunks):
    """Ghép các đoạn thành ngữ cảnh: dòng '[chunk_id] văn bản, Điều (tên), Khoản:' rồi nội dung ở dòng sau."""
    def head(c):
        where = f"{c['article']} ({c['article_title']})" if c.get("article_title") else c["article"]
        return f"[{c['chunk_id']}] {c['document']}, {where}" + (f", {c['clause']}" if c.get("clause") else "")
    return "\n\n".join(f"{head(c)}:\n{c['content']}" for c in chunks)


def route_messages(question, laws):
    """Messages cho nút route: phân loại câu hỏi và trích event_date, law_id, article. Đầu ra LLM là JSON."""
    # replace thay vì format: luật JSON trong ví dụ có ngoặc nhọn
    return _messages("route", ROUTE_RULES.replace("{laws}", law_list(laws)), f"Câu hỏi: {question}")


def grade_messages(question, evidence, queries):
    """Messages cho nút grade: đánh giá `evidence` đã đủ trả lời `question` chưa; `queries` là các truy vấn đã dùng."""
    return _messages("grade", GRADE_RULES, f"Câu hỏi: {question}\nCác truy vấn đã dùng: {'; '.join(queries)}\n\n"
                                           f"Đoạn trích:\n{format_context(evidence)}")


def generate_messages(question, evidence, event_date=None, unsupported=()):
    """Messages cho nút generate.

    Args:
        question: câu hỏi của người dùng.
        evidence: các chunk làm ngữ cảnh.
        event_date: ngày xảy ra sự việc (YYYY-MM-DD) hoặc None.
        unsupported: các câu bị verify gỡ hết căn cứ ở lần trước, để LLM sửa khi sinh lại.
    """
    parts = [f"Đoạn trích:\n{format_context(evidence)}"]
    if event_date:
        parts.append(f"Sự việc xảy ra ngày {event_date}.")
    parts.append(f"Câu hỏi: {question}")
    if unsupported:
        parts.append("Ở lần trả lời trước, các câu sau không được đoạn trích hỗ trợ; hãy sửa cho đúng đoạn trích "
                     "hoặc bỏ đi:\n" + "\n".join(f"- {s}" for s in unsupported))
    return _messages("generate", GENERATE_RULES, "\n\n".join(parts))


def verify_messages(pairs, by_id):
    """Messages cho verify(b): kiểm từng cặp (câu, đoạn được trích).

    Args:
        pairs: danh sách (chỉ số câu, câu, các mã) như citations.cited_sentences; câu được đánh số 1..n theo thứ tự.
        by_id: {chunk_id: chunk} của ngữ cảnh.
    """
    items = [f"Câu {n}: {sentence}\n" + "\n".join(f"  [{cid}] {by_id[cid]['content']}" for cid in ids)
             for n, (_, sentence, ids) in enumerate(pairs, 1)]
    return _messages("verify", VERIFY_RULES, "\n\n".join(items))
