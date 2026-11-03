"""Các nút của tác tử (spec mục 5). Mỗi nút nhận state và Deps, trả về phần state cần cập nhật."""
import re
from dataclasses import dataclass

from src.agent.state import MAX_EVIDENCE, MAX_REWRITES, TOP_K
from src.generation import citations, prompts
from src.retrieval.filters import ANY_DATE, check_date, is_valid_at

ROUTE_TYPES = {"situational", "direct", "out_of_scope"}
REFUSALS = {
    "out_of_scope": "Câu hỏi nằm ngoài phạm vi hệ thống. Hệ thống chỉ hỗ trợ Bộ luật Dân sự, Bộ luật Lao động, "
                    "Luật Doanh nghiệp và Luật Thương mại.",
    "no_evidence": "Không tìm thấy văn bản có hiệu lực tại thời điểm của tình huống trong kho dữ liệu.",
    "insufficient": "Không đủ căn cứ trong kho dữ liệu để trả lời câu hỏi này.",
}
NO_CITATION_NOTE = "(Câu trả lời chưa có căn cứ trích dẫn.)"


@dataclass(frozen=True)
class Deps:
    """Phụ thuộc của các nút: LLM, Retriever và nội dung laws.json."""

    llm: object  # src.generation.llm.LLM
    retriever: object  # có search(query, k, date) và get_article(law_id, number)
    laws: dict  # nội dung data/raw/laws.json


def _safe_date(value):
    try:
        return check_date(value)
    except (TypeError, ValueError):
        return None  # ngày LLM trả sai dạng: coi như không có, truy xuất theo văn bản còn hiệu lực


def _law_id(raw, laws):
    """Mã LLM trả ('BLLĐ 2012', 'blds-2015') về khóa trong laws.json; None nếu không khớp."""
    key = re.sub(r"[\s\-_.]", "", str(raw or "")).upper().replace("Đ", "D")
    return key if key in laws else None


def _direct_ref(out, laws):
    law_id = _law_id(out.get("law_id"), laws)
    raw = str(out.get("article") or "")
    # ưu tiên số đứng sau "Điều": "Khoản 2 Điều 35" là Điều 35 chứ không phải Điều 2
    article = re.search(r"Điều\s*(\d+[a-z]?)", raw, re.I) or re.search(r"(\d+[a-z]?)", raw, re.I)
    return {"law_id": law_id, "article": article.group(1).lower()} if law_id and article else None


def route(state, deps):
    """Nút route: 1 lượt LLM phân loại câu hỏi và trích ngày, văn bản, số Điều.

    Returns:
        {"route_type", "event_date", "direct_ref"}. JSON hỏng sau 2 lần thì mặc định situational;
        ngày sai dạng thành None; law_id/article không khớp kho thì direct_ref = None (rơi về truy xuất).
    """
    try:
        out = deps.llm.chat_json(prompts.route_messages(state["question"], deps.laws))
    except ValueError:
        out = {}  # JSON hỏng sau 2 lần: mặc định situational (spec mục 6)
    kind = out.get("type")
    kind = kind if isinstance(kind, str) and kind in ROUTE_TYPES else "situational"
    return {"route_type": kind, "event_date": _safe_date(out.get("event_date")),
            "direct_ref": _direct_ref(out, deps.laws) if kind == "direct" else None}


def _search_date(state):
    """Ngày dùng để lọc hiệu lực theo chính sách RQ4 trong state (event | current | any)."""
    return {"event": state["event_date"], "current": None, "any": ANY_DATE}[state["date_policy"]]


def lookup_article(state, deps):
    """Nút lookup_article (0 lượt LLM): lấy toàn văn Điều theo `direct_ref`.

    Returns:
        {"evidence": [Điều]}; [] nếu không có Điều đó hoặc văn bản không có hiệu lực tại `event_date`.
        Chính sách event mà không có ngày sự việc: trả Điều người dùng đã nêu đích danh, kể cả văn bản đã hết
        hiệu lực (vd "Theo BLLĐ 2012, Điều 104…"); chính sách current vẫn chỉ nhận văn bản còn hiệu lực.
    """
    ref = state["direct_ref"]
    article = deps.retriever.get_article(ref["law_id"], ref["article"])
    named_without_date = state["date_policy"] == "event" and state["event_date"] is None
    date = ANY_DATE if named_without_date else _search_date(state)
    # văn bản chưa có hiệu lực (hoặc đã hết) tại event_date: coi như không có, đồ thị rơi về retrieve rồi từ chối
    return {"evidence": [article] if article and is_valid_at(article, date) else []}


def _merge(old, new):
    """Gộp bằng chứng các vòng (giữ thứ tự, bỏ trùng): vòng viết lại không làm mất đoạn đã tìm được."""
    seen = {c["chunk_id"] for c in old}
    return (old + [c for c in new if c["chunk_id"] not in seen])[:MAX_EVIDENCE]


def retrieve(state, deps):
    """Nút retrieve (0 lượt LLM): tìm bằng truy vấn mới nhất, lọc hiệu lực theo `event_date`, gộp vào bằng chứng."""
    # không lọc theo lĩnh vực: router đoán sai lĩnh vực không kéo theo truy xuất sai (spec mục 5)
    found = deps.retriever.search(state["queries"][-1], k=TOP_K, date=_search_date(state))
    return {"queries": state["queries"], "evidence": _merge(state["evidence"], found)}


def refuse(state, deps):
    """Nút refuse: trả lời từ chối theo lý do (out_of_scope, no_evidence hoặc insufficient)."""
    if state["route_type"] == "out_of_scope":
        reason = "out_of_scope"
    elif not state["evidence"]:
        reason = "no_evidence"
    else:
        reason = "insufficient"
    return {"answer": REFUSALS[reason], "refused": True, "citations": [], "refuse_reason": reason}


def _is_false(value):
    return value is False or str(value).strip().lower() in {"false", "0", "no"}


def grade(state, deps):
    """Nút grade: 1 lượt LLM đánh giá bằng chứng đã đủ chưa.

    Returns:
        {"sufficient": True, "rewrite": False} khi đủ (hoặc JSON hỏng: mặc định đủ);
        {"sufficient": False, "rewrite": True, "queries": [...], "n_rewrites": n+1} khi cần viết lại;
        {"sufficient": False, "rewrite": False} khi hết MAX_REWRITES vòng hoặc truy vấn mới rỗng/trùng.
    """
    try:
        out = deps.llm.chat_json(prompts.grade_messages(state["question"], state["evidence"], state["queries"]))
    except ValueError:
        return {"sufficient": True, "rewrite": False}  # JSON hỏng: mặc định đủ (spec mục 6)
    if not _is_false(out.get("sufficient")):
        return {"sufficient": True, "rewrite": False}
    new_query = str(out.get("new_query") or "").strip()
    n = state["n_rewrites"]
    if n >= MAX_REWRITES or not new_query or new_query in state["queries"]:
        return {"sufficient": False, "rewrite": False}  # truy vấn trùng/rỗng: viết lại nữa cũng vô ích
    return {"sufficient": False, "rewrite": True, "queries": state["queries"] + [new_query], "n_rewrites": n + 1}


def generate(state, deps):
    """Nút generate: 1 lượt LLM sinh câu trả lời có gắn [chunk_id].

    Returns:
        {"answer", "insufficient", "n_generations"}; LLM trả KHÔNG_ĐỦ_CĂN_CỨ hoặc rỗng thì insufficient = True.
    """
    messages = prompts.generate_messages(state["question"], state["evidence"], state["event_date"],
                                         state["unsupported"])
    text = deps.llm.chat(messages).strip().removeprefix("Trả lời:").strip()
    n = state["n_generations"] + 1
    if not text or prompts.INSUFFICIENT in text:
        return {"answer": "", "insufficient": True, "n_generations": n}
    return {"answer": text, "insufficient": False, "n_generations": n}


def _unsupported_pairs(pairs, by_id, deps):
    """{chỉ số câu: {mã}} các cặp LLM cho là không được hỗ trợ; mục sai dạng bị bỏ qua, JSON hỏng thì không gỡ gì."""
    try:
        out = deps.llm.chat_json(prompts.verify_messages(pairs, by_id))
    except ValueError:
        return {}
    items = out.get("unsupported")
    verdicts = {}
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        try:
            n = int(item.get("sentence"))
        except (TypeError, ValueError):
            continue
        if 1 <= n <= len(pairs) and item.get("chunk_id") in pairs[n - 1][2]:
            verdicts.setdefault(pairs[n - 1][0], set()).add(item["chunk_id"])
    return verdicts


def _citation(chunk):
    return {key: chunk.get(key) for key in ("chunk_id", "document", "article", "clause", "content")}


def verify(state, deps, use_llm=True):
    """Nút verify: (a) gỡ mã ngoài ngữ cảnh bằng regex; (b) nếu use_llm, 1 lượt LLM kiểm từng cặp (câu, đoạn).

    Câu mất hết căn cứ: sinh lại 1 lần (`regenerate`), sau đó gắn nhãn "(chưa có căn cứ)".

    Args:
        state: cần `answer`, `evidence`, `n_generations`.
        deps: phụ thuộc của nút.
        use_llm: False thì chỉ chạy (a) (cấu hình no_verify và baseline).

    Returns:
        Khi cần sinh lại: {"answer", "removed", "regenerate": True, "unsupported": [câu gốc]}.
        Khi xong: thêm "citations" (đoạn được trích) và "refused": False.
    """
    draft = state["answer"]
    by_id = {c["chunk_id"]: c for c in state["evidence"]}
    answer, removed = citations.strip_unknown(citations.normalize_ids(draft, by_id), by_id)
    if use_llm:
        pairs = citations.cited_sentences(answer)
        verdicts = _unsupported_pairs(pairs, by_id, deps) if pairs else {}
        removed = removed + [cid for ids in verdicts.values() for cid in sorted(ids)]
        answer = citations.drop_pairs(answer, verdicts)
    lost = citations.lost_sentences(draft, answer)
    if lost and use_llm and state["n_generations"] < 2:
        parts = citations.sentences(draft)
        return {"answer": answer, "removed": removed, "regenerate": True, "unsupported": [parts[i] for i in lost]}
    answer = citations.label_sentences(answer, lost)
    ids = citations.cited_ids(answer)
    if not ids:
        answer = f"{answer}\n\n{NO_CITATION_NOTE}"
    return {"answer": answer, "removed": removed, "regenerate": False, "unsupported": [],
            "citations": [_citation(by_id[cid]) for cid in ids], "refused": False}
