"""Điểm vào giao diện NiceGUI.

Chạy (từ thư mục gốc dự án):
    uvicorn src.api.main:app --port 8000              # terminal 1: backend
    python -m src.ui.web.main                         # terminal 2: giao diện, mở http://127.0.0.1:8080
Biến môi trường: API_URL (mặc định http://localhost:8000), FRONTEND_HOST, FRONTEND_PORT, API_TIMEOUT.
"""
from nicegui import ui

from src.ui.web.api.client import LegalQAApiClient
from src.ui.web.config import FRONTEND_HOST, FRONTEND_PORT
from src.ui.web.pages.chat import chat_page


@ui.page("/")
async def index() -> None:
    await chat_page(LegalQAApiClient(enable_local_fallback=True))


def main() -> None:
    ui.run(title="Hỏi đáp pháp luật Việt Nam", host=FRONTEND_HOST, port=FRONTEND_PORT, reload=False,
           show=False, favicon="⚖️", language="vi")


if __name__ in {"__main__", "__mp_main__"}:
    main()

