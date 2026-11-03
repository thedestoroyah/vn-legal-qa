"""Giao diện Streamlit: gọi API khi đặt API_URL, nếu không thì dùng phản hồi mẫu (Phụ lục A.5).

Chạy:
    streamlit run src/ui/app.py                                   # phản hồi mẫu, không cần mô hình
    API_URL=http://localhost:8000 streamlit run src/ui/app.py     # gọi API thật (uvicorn src.api.main:app)
"""
import json
import os
import sys
from pathlib import Path

import requests
import streamlit as st

# Thêm thư mục hiện tại để import
sys.path.insert(0, str(Path(__file__).parent))
from article_view import article_key, clause_number, split_clauses

API_URL = os.environ.get("API_URL", "").rstrip("/")  # trống: dùng phản hồi mẫu (làm UI không cần chạy mô hình)
TIMEOUT = 180  # giây; tác tử free tier mất 10–60 s mỗi câu
SAMPLES = Path(__file__).with_name("samples")
SAMPLE_NAMES = ["answered", "refused", "partial"]
ARTICLES = Path(__file__).with_name("sample_articles.json")
DISCLAIMER = "Thông tin chỉ mang tính tham khảo, không thay thế tư vấn pháp lý."
NO_BASIS = "(chưa có căn cứ)"
ROUTES = {"situational": "tình huống", "direct": "tra cứu trực tiếp", "out_of_scope": "ngoài phạm vi"}
REASONS = {"out_of_scope": "ngoài phạm vi", "no_evidence": "không có văn bản hiệu lực tại thời điểm",
           "insufficient": "không đủ căn cứ"}


class ApiError(Exception):
    """Lỗi gọi API, mang câu thông báo để hiển thị cho người dùng."""


def ask(question):
    """Phản hồi Phụ lục A.5 cho một câu hỏi: từ API nếu có API_URL, nếu không thì phản hồi mẫu chọn ở thanh bên."""
    if not API_URL:
        name = st.session_state.get("sample", "answered")
        return json.loads((SAMPLES / f"{name}.json").read_text(encoding="utf-8"))
    try:
        r = requests.post(f"{API_URL}/api/ask", json={"question": question, "config": "full"}, timeout=TIMEOUT)
    except requests.Timeout:
        raise ApiError("Máy chủ trả lời quá lâu. Vui lòng thử lại sau.")
    except requests.RequestException:
        raise ApiError("Không kết nối được máy chủ hỏi đáp. Kiểm tra API đã chạy chưa.")
    if r.status_code == 422:
        raise ApiError("Câu hỏi không hợp lệ (rỗng hoặc dài quá 1000 ký tự).")
    if r.status_code != 200:
        try:
            detail = r.json().get("detail")
        except ValueError:
            detail = None
        raise ApiError(detail if isinstance(detail, str) else f"Lỗi máy chủ ({r.status_code}).")
    return r.json()


def get_article(chunk_id):
    """Toàn văn Điều chứa chunk_id (dạng chunk cấp Điều), hoặc None nếu không lấy được."""
    if not API_URL:
        if not ARTICLES.exists():
            return None
        return json.loads(ARTICLES.read_text(encoding="utf-8")).get(article_key(chunk_id))
    law_id, number = article_key(chunk_id).split("_Dieu")
    try:
        r = requests.get(f"{API_URL}/api/article/{law_id}/{number}", timeout=30)
    except requests.RequestException:
        return None
    return r.json() if r.status_code == 200 else None


def api_health():
    """Tên model của API nếu API đang chạy, ngược lại None."""
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        return r.json().get("model") if r.status_code == 200 else None
    except (requests.RequestException, ValueError):
        return None


def step_note(step):
    """Một dòng tóm tắt dễ đọc cho mỗi bước trace."""
    o = step.get("output") or {}
    node = step.get("node")
    if node == "route":
        route = o.get("route_type")
        note = f"Loại câu hỏi: {ROUTES.get(route, route)}"
        if o.get("event_date"):
            note += f" · ngày sự việc {o['event_date']}"
        if o.get("direct_ref"):
            note += f" · điều luật được hỏi: {o['direct_ref']}"
        return note
    if node == "lookup_article":
        evidence = o.get("evidence") or []
        return f"Tra cứu trực tiếp: {', '.join(evidence)}" if evidence else "Không tìm thấy điều luật được hỏi"
    if node == "retrieve":
        queries = o.get("queries") or []
        extra = f" · truy vấn viết lại: “{queries[-1]}”" if len(queries) > 1 else ""
        return f"Tìm được {len(o.get('evidence') or [])} đoạn{extra}"
    if node == "grade":
        if o.get("sufficient"):
            return "Đủ căn cứ"
        return "Chưa đủ, viết lại truy vấn" if o.get("rewrite") else "Chưa đủ, dừng"
    if node == "generate":
        if o.get("insufficient"):
            return "Mô hình báo không đủ căn cứ để trả lời"
        return f"Sinh câu trả lời (lần {o.get('n_generations', 1)})"
    if node == "verify":
        removed = ", ".join(o.get("removed") or []) or "không"
        return f"Trích dẫn bị gỡ: {removed}" + (" · yêu cầu sinh lại" if o.get("regenerate") else "")
    if node == "refuse":
        reason = o.get("refuse_reason")
        return f"Từ chối: {REASONS.get(reason, reason)}"
    return ""


def citation_label(c):
    return f"{c['document']} – {c['article']}" + (f", {c['clause']}" if c.get("clause") else "")


st.set_page_config(page_title="Hỏi đáp pháp luật", layout="wide")
st.session_state.setdefault("history", [])
st.session_state.setdefault("selected", None)

if API_URL:
    model = api_health()
    if model:
        st.sidebar.success(f"API: {API_URL}\n\nModel: {model}")
    else:
        st.sidebar.error(f"Không kết nối được API tại {API_URL}")
else:
    st.sidebar.selectbox("Phản hồi mẫu", SAMPLE_NAMES, key="sample")
    st.sidebar.caption("Chưa đặt API_URL: giao diện dùng phản hồi mẫu.")

chat_col, panel_col = st.columns([2, 1])

with chat_col:
    st.title("Hỏi đáp pháp luật Việt Nam")
    st.caption(DISCLAIMER)
    for turn, (question, resp) in enumerate(st.session_state["history"]):
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            if resp["refused"]:
                st.warning(resp["answer"])
            else:
                st.markdown(resp["answer"].replace(NO_BASIS, f":orange[{NO_BASIS}]"))
            for c in resp["citations"]:
                if st.button(citation_label(c), key=f"{turn}-{c['chunk_id']}"):
                    st.session_state["selected"] = c
            with st.expander("Các bước tác tử"):
                for step in resp["trace"]:
                    st.write(f"**{step['node']}** · {step['ms']} ms · {step['llm_calls']} lượt gọi LLM — {step_note(step)}")
                    st.json(step["output"], expanded=False)
    question = st.chat_input("Nhập câu hỏi pháp luật...")
    if question:
        with st.spinner("Đang tra cứu và soạn câu trả lời (có thể mất tới 1 phút)..."):
            try:
                st.session_state["history"].append((question, ask(question)))
            except ApiError as e:
                st.error(str(e))
                st.stop()
        st.rerun()

with panel_col:
    c = st.session_state["selected"]
    if c is None:
        st.info("Bấm vào một trích dẫn để xem nguyên văn điều luật.")
    else:
        art = get_article(c["chunk_id"])
        if art is None:
            where = "trong dữ liệu mẫu" if not API_URL else "từ máy chủ"
            st.warning(f"Chưa lấy được nguyên văn của {c['chunk_id']} {where}.")
        else:
            st.subheader(f"{art['document']} – {art['article']}")
            st.caption(art.get("article_title") or "")
            target = clause_number(c.get("clause"))
            for number, text in split_clauses(art["content"]):
                (st.success if number is not None and number == target else st.markdown)(text)
