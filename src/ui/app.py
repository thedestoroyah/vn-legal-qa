"""Khung giao diện (Sprint 2 & 3): dùng phản hồi mẫu theo Phụ lục A.5, hiển thị nguyên văn điều luật."""
import json
import sys
from pathlib import Path

import streamlit as st

# Thêm thư mục hiện tại để import
sys.path.insert(0, str(Path(__file__).parent))
from article_view import article_key, clause_number, split_clauses

SAMPLE = Path(__file__).with_name("sample_response.json")
ARTICLES = Path(__file__).with_name("sample_articles.json")
DISCLAIMER = "Thông tin chỉ mang tính tham khảo, không thay thế tư vấn pháp lý."


def ask(question):
    # shortcut: trả phản hồi mẫu cố định; Sprint 4 thay bằng gọi POST /api/ask
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def get_article(chunk_id):
    # shortcut: đọc file mẫu; Sprint 4 thay bằng GET /api/article/{law_id}/{article}
    if not ARTICLES.exists():
        return None
    articles = json.loads(ARTICLES.read_text(encoding="utf-8"))
    return articles.get(article_key(chunk_id))


def citation_label(c):
    return f"{c['document']} – {c['article']}" + (f", {c['clause']}" if c.get("clause") else "")


st.set_page_config(page_title="Hỏi đáp pháp luật", layout="wide")
st.session_state.setdefault("history", [])
st.session_state.setdefault("selected", None)
chat_col, panel_col = st.columns([2, 1])

with chat_col:
    st.title("Hỏi đáp pháp luật Việt Nam")
    st.caption(DISCLAIMER)
    for turn, (question, resp) in enumerate(st.session_state["history"]):
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            (st.warning if resp["refused"] else st.markdown)(resp["answer"])
            for c in resp["citations"]:
                if st.button(citation_label(c), key=f"{turn}-{c['chunk_id']}"):
                    st.session_state["selected"] = c
            with st.expander("Các bước tác tử"):
                for step in resp["trace"]:
                    st.write(f"**{step['node']}** · {step['ms']} ms · {step['llm_calls']} lượt gọi LLM")
                    st.json(step["output"], expanded=False)
    question = st.chat_input("Nhập câu hỏi pháp luật...")
    if question:
        st.session_state["history"].append((question, ask(question)))
        st.rerun()

with panel_col:
    c = st.session_state["selected"]
    if c is None:
        st.info("Bấm vào một trích dẫn để xem nguyên văn điều luật.")
    else:
        art = get_article(c["chunk_id"])
        if art is None:
            st.warning(f"Chưa có nguyên văn của {c['chunk_id']} trong dữ liệu mẫu.")
        else:
            st.subheader(f"{art['document']} – {art['article']}")
            st.caption(art["article_title"])
            target = clause_number(c.get("clause"))
            for number, text in split_clauses(art["content"]):
                (st.success if number is not None and number == target else st.markdown)(text)
