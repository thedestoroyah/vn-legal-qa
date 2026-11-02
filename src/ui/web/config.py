"""Cấu hình môi trường và danh mục văn bản cho giao diện NiceGUI."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv không bắt buộc
    pass

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LAWS_JSON_PATH = PROJECT_ROOT / "data" / "raw" / "laws.json"
STATIC_DIR = Path(__file__).resolve().parent / "static"

# Địa chỉ FastAPI backend (src/api/main.py)
API_URL: str = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")

# Thời gian chờ (giây); tác tử free tier mất 10–60 s mỗi câu
ASK_TIMEOUT: float = float(os.environ.get("API_TIMEOUT", "180"))
ARTICLE_TIMEOUT: float = 30.0
HEALTH_TIMEOUT: float = 5.0

FRONTEND_HOST: str = os.environ.get("FRONTEND_HOST", "127.0.0.1")
FRONTEND_PORT: int = int(os.environ.get("FRONTEND_PORT", "8080"))

MAX_QUESTION = 1000  # khớp src/api/main.py: MAX_QUESTION

# Khóa hợp lệ của AskRequest.config (src/agent/state.py: CONFIGS)
AGENT_CONFIGS: dict[str, str] = {
    "full": "Đầy đủ (full)",
    "no_router": "Không định tuyến (no_router)",
    "no_grading": "Không chấm bằng chứng (no_grading)",
    "no_verify": "Không kiểm chứng LLM (no_verify)",
    "baseline": "RAG cơ sở (baseline)",
}

APP_TITLE = "Hỏi đáp pháp luật Việt Nam"
APP_SUBTITLE = "Agentic-RAG · 5 văn bản luật"
DISCLAIMER = "Thông tin chỉ mang tính tham khảo, không thay thế tư vấn pháp lý."
NO_BASIS = "(chưa có căn cứ)"

# Tên bước trace (src/agent/nodes.py) -> nhãn tiếng Việt
NODE_LABELS: dict[str, str] = {
    "route": "Phân tích câu hỏi",
    "lookup_article": "Tra cứu trực tiếp Điều luật",
    "retrieve": "Truy xuất văn bản",
    "grade": "Đánh giá bằng chứng",
    "generate": "Sinh câu trả lời",
    "verify": "Kiểm chứng trích dẫn",
    "refuse": "Từ chối trả lời",
}
NODE_ICONS: dict[str, str] = {
    "route": "alt_route",
    "lookup_article": "menu_book",
    "retrieve": "search",
    "grade": "fact_check",
    "generate": "edit_note",
    "verify": "verified",
    "refuse": "block",
}
ROUTES: dict[str, str] = {
    "situational": "tình huống thực tế",
    "temporal": "theo mốc thời gian",
    "direct": "tra cứu trực tiếp",
    "out_of_scope": "ngoài phạm vi",
}
REASONS: dict[str, str] = {
    "out_of_scope": "Câu hỏi nằm ngoài phạm vi 5 văn bản pháp luật của hệ thống",
    "no_evidence": "Không tìm thấy văn bản có hiệu lực tại thời điểm tra cứu",
    "insufficient": "Bằng chứng truy xuất được chưa đủ căn cứ pháp lý để kết luận",
}

# Các bước chuẩn hiển thị khi đang xử lý (loading)
PIPELINE_PREVIEW_STEPS: list[tuple[str, str]] = [
    ("alt_route", "Phân tích câu hỏi"),
    ("search", "Truy xuất văn bản"),
    ("fact_check", "Đánh giá bằng chứng"),
    ("edit_note", "Sinh câu trả lời"),
    ("verified", "Kiểm chứng trích dẫn"),
]

# Câu hỏi gợi ý (lấy từ eval/test_cases.json và tài liệu sprint), chỉ điền vào ô nhập, không phải dữ liệu trả lời
SAMPLE_QUESTIONS: list[tuple[str, str]] = [
    ("Tra cứu trực tiếp", "Điều 357 Bộ luật Dân sự 2015 quy định gì?"),
    ("Tình huống thực tế", "Bên mua trả tiền chậm có phải trả lãi không?"),
    (
        "Hiệu lực theo thời gian",
        "Vào tháng 5/2020, công ty giao kết hợp đồng lao động theo mùa vụ 6 tháng để thu hoạch nông sản "
        "thì loại hợp đồng này có đúng quy định pháp luật không?",
    ),
    ("Ngoài phạm vi", "Mức phạt vượt đèn đỏ đối với xe máy hiện nay là bao nhiêu?"),
]


def load_laws_catalog() -> dict[str, dict[str, Any]]:
    """Danh mục văn bản trong data/raw/laws.json (cùng file backend dùng); {} nếu không đọc được."""
    try:
        return json.loads(LAWS_JSON_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


LAWS_CATALOG: dict[str, dict[str, Any]] = load_laws_catalog()
