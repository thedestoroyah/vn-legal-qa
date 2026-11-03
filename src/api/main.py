"""API hỏi đáp pháp luật (Phụ lục A.5): POST /api/ask, GET /api/article/{law_id}/{article}, GET /health.

Chạy: uvicorn src.api.main:app --port 8000   (nạp mô hình một lần khi khởi động, ~30 s)
"""
import logging
import threading
from contextlib import asynccontextmanager
from typing import Literal

import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from src.agent.state import CONFIGS

log = logging.getLogger("vn_legal_qa.api")
MAX_QUESTION = 1000
# người dùng đang chờ trên giao diện: thà báo lỗi sớm còn hơn treo 3 phút; eval chạy nền vẫn thử lại 8 lần
API_LLM_MAX_RETRIES = 2
# Gemini quá tải đôi khi trả lời rất chậm thay vì báo 503: chặn mỗi lượt gọi ở 30 s để không giữ khóa quá lâu
API_LLM_TIMEOUT = 30
LLM_ERROR = "Dịch vụ mô hình ngôn ngữ đang quá tải hoặc tạm thời không khả dụng. Vui lòng thử lại sau ít phút."


class AskRequest(BaseModel):
    """Thân request của POST /api/ask; khoảng trắng đầu cuối bị bỏ trước khi kiểm tra độ dài."""

    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=MAX_QUESTION)
    config: Literal[tuple(CONFIGS)] = "full"


def _load_real_agent():
    from src.agent.run import load_agent
    return load_agent(max_retries=API_LLM_MAX_RETRIES, timeout=API_LLM_TIMEOUT)


def create_app(load=_load_real_agent):
    """Tạo app FastAPI.

    Args:
        load: hàm không tham số trả Agent; gọi một lần khi app khởi động (test truyền tác tử giả).
    """
    state = {}
    # LLM (bộ đếm lượt gọi trong trace, giãn cách RPM, cache) không an toàn đa luồng: phục vụ tuần tự từng câu hỏi
    lock = threading.Lock()

    @asynccontextmanager
    async def lifespan(app):
        state["agent"] = load()
        yield

    app = FastAPI(title="Hỏi đáp pháp luật Việt Nam", lifespan=lifespan)

    @app.post("/api/ask")
    def ask(req: AskRequest):
        """Trả lời một câu hỏi theo Phụ lục A.5; LLM lỗi sau khi đã thử lại thì 503."""
        try:
            with lock:
                return state["agent"].run(req.question, req.config)
        except openai.APIError:
            log.exception("LLM lỗi khi trả lời câu hỏi: %.100s", req.question)
            raise HTTPException(status_code=503, detail=LLM_ERROR)

    @app.get("/api/article/{law_id}/{article}")
    def article(law_id: str, article: str):
        """Toàn văn một Điều (chunk cấp Điều); 404 nếu không có."""
        found = state["agent"].deps.retriever.get_article(law_id, article)
        if found is None:
            raise HTTPException(status_code=404, detail=f"Không có {law_id} Điều {article}")
        return found

    @app.get("/health")
    def health():
        """Trạng thái dịch vụ và tên model LLM của tác tử."""
        return {"status": "ok", "model": state["agent"].deps.llm.model}

    return app


app = create_app()
