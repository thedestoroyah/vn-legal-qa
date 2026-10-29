import pytest

from src.generation import prompts
from src.generation.prompts import ROLES

LAWS = {
    "BLDS2015": {"document": "Bộ luật Dân sự 2015", "effective_date": "2017-01-01", "expiry_date": None},
    "BLLD2012": {"document": "Bộ luật Lao động 2012", "effective_date": "2013-05-01", "expiry_date": "2021-01-01"},
}
A = "BLDS2015_Dieu357_Khoan1"
EV = [{"chunk_id": A, "document": "Bộ luật Dân sự 2015", "article": "Điều 357",
       "article_title": "Trách nhiệm do chậm thực hiện nghĩa vụ trả tiền", "clause": "Khoản 1",
       "content": "Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó phải trả lãi."}]
ALL = {
    "route": prompts.route_messages("câu hỏi", LAWS),
    "grade": prompts.grade_messages("câu hỏi", EV, ["câu hỏi"]),
    "generate": prompts.generate_messages("câu hỏi", EV),
    "verify": prompts.verify_messages([(0, f"Có [{A}].", [A])], {A: EV[0]}),
}


@pytest.mark.parametrize("node", list(ROLES))
def test_every_prompt_starts_with_its_role_and_has_two_examples(node):
    system = ALL[node][0]
    assert system["role"] == "system" and system["content"].startswith(ROLES[node])
    assert system["content"].count("Ví dụ") >= 2
    assert ALL[node][-1]["role"] == "user"


def test_roles_are_not_prefixes_of_each_other():
    roles = list(ROLES.values())
    assert not any(a != b and b.startswith(a) for a in roles for b in roles)


def test_route_prompt_lists_laws_with_validity():
    system, user = ALL["route"]
    assert "BLLD2012: Bộ luật Lao động 2012 (hiệu lực từ 2013-05-01, hết hiệu lực từ 2021-01-01)" in system["content"]
    assert "BLDS2015: Bộ luật Dân sự 2015 (hiệu lực từ 2017-01-01, còn hiệu lực)" in system["content"]
    assert "{laws}" not in system["content"]
    assert user["content"] == "Câu hỏi: câu hỏi"


def test_format_context_shows_id_article_clause_and_content():
    assert prompts.format_context(EV) == (
        f"[{A}] Bộ luật Dân sự 2015, Điều 357 (Trách nhiệm do chậm thực hiện nghĩa vụ trả tiền), Khoản 1:\n"
        "Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó phải trả lãi.")


def test_format_context_article_chunk_has_no_clause():
    art = {**EV[0], "chunk_id": "BLDS2015_Dieu357", "clause": None}
    assert prompts.format_context([art]).startswith("[BLDS2015_Dieu357] Bộ luật Dân sự 2015, Điều 357 (")


def test_grade_prompt_shows_previous_queries():
    user = prompts.grade_messages("q", EV, ["q", "lãi chậm trả"])[-1]["content"]
    assert "Các truy vấn đã dùng: q; lãi chậm trả" in user and A in user


def test_generate_prompt_includes_date_and_regeneration_feedback():
    user = prompts.generate_messages("q", EV, "2020-07-01", ["Câu sai [X]."])[-1]["content"]
    assert "Sự việc xảy ra ngày 2020-07-01." in user
    assert "- Câu sai [X]." in user
    assert user.index("Đoạn trích:") < user.index("Câu hỏi: q")


def test_generate_prompt_without_extras_has_no_feedback_section():
    user = ALL["generate"][-1]["content"]
    assert "lần trả lời trước" not in user and "Sự việc xảy ra" not in user


def test_verify_prompt_numbers_pairs_from_one():
    B = "BLDS2015_Dieu357_Khoan2"
    by_id = {A: EV[0], B: {**EV[0], "chunk_id": B, "content": "Lãi suất theo thỏa thuận."}}
    user = prompts.verify_messages([(2, f"Một [{A}].", [A]), (6, f"Hai [{B}].", [B])], by_id)[-1]["content"]
    head = "Bộ luật Dân sự 2015, Điều 357 (Trách nhiệm do chậm thực hiện nghĩa vụ trả tiền)"
    assert user == (f"Câu 1: Một [{A}].\n  [{A}] {head}, Khoản 1: Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó "
                    f"phải trả lãi.\n\nCâu 2: Hai [{B}].\n  [{B}] {head}, Khoản 1: Lãi suất theo thỏa thuận.")


def test_verify_rules_count_application_to_the_case_as_support():
    system = ALL["verify"][0]["content"]
    assert "tên Điều" in system and "áp dụng" in system and "mâu thuẫn" in system


def test_route_prompt_scopes_by_legal_issue_not_keyword():
    system = ALL["route"][0]["content"]
    # bối cảnh giao thông/đất đai/gia đình nhưng hỏi bồi thường, hợp đồng, tài sản, thừa kế, đại diện vẫn là situational
    assert "thừa kế" in system and "bồi thường thiệt hại" in system
    assert "chỉ là bối cảnh" in system
    assert '"situational"' in system[system.index("va vào"):]  # ví dụ bối cảnh giao thông được xếp situational
