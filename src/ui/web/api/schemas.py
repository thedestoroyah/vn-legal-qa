"""Schema phản hồi của src/api/main.py (Phụ lục A.5). Trường tùy chọn có mặc định để thiếu dữ liệu không làm vỡ UI."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.ui.web.config import NO_BASIS


class _Base(BaseModel):
    model_config = ConfigDict(extra="ignore")


class HealthResponse(_Base):
    """GET /health."""

    status: str = "ok"
    model: str = ""


class CitationItem(_Base):
    """Một phần tử `citations` (src/agent/nodes.py: _citation)."""

    chunk_id: str
    document: str = ""
    article: str = ""
    clause: str | None = None
    content: str = ""


class RetrievedChunk(_Base):
    chunk_id: str
    score: float | None = None


class TraceStep(_Base):
    """Một bước trace (src/agent/graph.py: _traced)."""

    node: str
    output: dict[str, Any] = Field(default_factory=dict)
    ms: int = 0
    llm_calls: int = 0


class AskResponse(_Base):
    """POST /api/ask."""

    answer: str = ""
    refused: bool = False
    citations: list[CitationItem] = Field(default_factory=list)
    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)
    trace: list[TraceStep] = Field(default_factory=list)

    def step(self, node: str) -> dict[str, Any]:
        """Output của bước đầu tiên tên `node`; {} nếu không có."""
        return next((s.output or {} for s in self.trace if s.node == node), {})

    @property
    def route_type(self) -> str | None:
        return self.step("route").get("route_type")

    @property
    def event_date(self) -> str | None:
        """Ngày sự việc do nút route trích ra (backend đã chuẩn hóa YYYY-MM-DD hoặc None)."""
        value = self.step("route").get("event_date")
        return str(value) if value else None

    @property
    def refuse_reason(self) -> str | None:
        return self.step("refuse").get("refuse_reason")

    @property
    def status(self) -> str:
        """answered | partial | refused — chỉ đọc cờ và nhãn backend đã gắn, không tự đánh giá."""
        if self.refused:
            return "refused"
        return "partial" if NO_BASIS in self.answer or not self.citations else "answered"

    @property
    def total_ms(self) -> int:
        return sum(max(0, s.ms) for s in self.trace)

    @property
    def total_llm_calls(self) -> int:
        return sum(max(0, s.llm_calls) for s in self.trace)


class ArticleResponse(_Base):
    """GET /api/article/{law_id}/{article}: một chunk cấp Điều."""

    chunk_id: str
    law_id: str | None = None
    document: str = ""
    number: str | None = None
    status: str | None = None
    effective_from: int | None = None
    effective_to: int | None = None
    article: str = ""
    article_title: str | None = None
    content: str = ""

