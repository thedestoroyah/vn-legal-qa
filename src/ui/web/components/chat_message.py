"""Một lượt hỏi đáp: câu hỏi, trạng thái chờ / lỗi thân thiện, câu trả lời, sao chép, đánh giá và 3 khu vực chi tiết."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
import re

from nicegui import ui

from src.ui.web.api.schemas import AskResponse, CitationItem
from src.ui.web.components.agent_timeline import agent_timeline, pending_pipeline
from src.ui.web.components.citation_card import citation_label, citation_list, copy_text
from src.ui.web.components.validity_card import validity_card
from src.ui.web.config import AGENT_CONFIGS, NO_BASIS, REASONS, ROUTES

_ID_RE = re.compile(r"\[([A-Za-z]+\d{4}_Dieu\w+?)\]")


@dataclass
class Turn:
    question: str
    config: str
    asked_at: datetime = field(default_factory=datetime.now)
    response: AskResponse | None = None
    error: str | None = None
    error_hint: str = ""
    feedback: str | None = None  # "up" | "down" | None

    @property
    def pending(self) -> bool:
        return self.response is None and self.error is None


def answer_markdown(answer: str) -> str:
    """Mã [chunk_id] thành `code` (tránh markdown hiểu dấu _ là in nghiêng); nhãn chưa có căn cứ in đậm."""
    text = _ID_RE.sub(r"`[\1]`", answer)
    return text.replace(NO_BASIS, f"**⚠ {NO_BASIS}**")


def format_turn_for_copy(turn: Turn) -> str:
    """Định dạng nội dung câu trả lời kèm danh sách căn cứ để sao chép."""
    if turn.response is None:
        return turn.question
    lines = [
        f"Câu hỏi: {turn.question}",
        "",
        f"Trả lời:\n{turn.response.answer}",
    ]
    if turn.response.citations:
        lines.append("\nCăn cứ pháp lý:")
        for c in turn.response.citations:
            lines.append(f"- {citation_label(c)} [{c.chunk_id}]: {c.content}")
    return "\n".join(lines)


def _status_badges(resp: AskResponse) -> None:
    if resp.route_type:
        route_label = ROUTES.get(resp.route_type, resp.route_type).capitalize()
        ui.badge(route_label, color="blue-grey-1", text_color="blue-grey-9").classes("text-xs px-2 py-0.5")
    if resp.total_ms > 0:
        ui.badge(f"{resp.total_ms / 1000:.1f}s", color="slate-100", text_color="slate-700").classes(
            "text-xs font-mono px-2 py-0.5"
        )
    status = resp.status
    if status == "refused":
        ui.badge("Từ chối trả lời", color="grey-7").classes("text-xs px-2.5 py-0.5")
    elif status == "partial":
        ui.badge("Có ý chưa có căn cứ", color="orange").classes("text-xs px-2.5 py-0.5")
    else:
        ui.badge(f"Có căn cứ · {len(resp.citations)} trích dẫn", color="positive").classes(
            "text-xs px-2.5 py-0.5"
        )


def render_turn(
    turn: Turn,
    on_open: Callable[[CitationItem], Awaitable[None]],
    elapsed_source: object,
    on_retry: Callable[[Turn], Awaitable[None]] | None = None,
    on_feedback: Callable[[Turn, str], None] | None = None,
) -> None:
    with ui.column().classes("w-full gap-2.5 turn-animate"):
        # Bong bóng câu hỏi người dùng (căn phải hiện đại)
        with ui.row().classes("w-full justify-end"):
            with ui.card().classes("user-bubble shadow-sm max-w-2xl p-3"):
                ui.label(turn.question).classes("text-sm text-white whitespace-pre-line leading-relaxed")
                with ui.row().classes("items-center justify-end gap-2 mt-1 text-[11px] text-blue-100"):
                    ui.label(f"{turn.asked_at:%H:%M} · {AGENT_CONFIGS.get(turn.config, turn.config)}")
                    ui.button(
                        icon="content_copy",
                        on_click=lambda q=turn.question: copy_text(q, "Đã sao chép câu hỏi"),
                    ).props("flat round dense size=xs color=white").tooltip("Sao chép câu hỏi")

        # Thẻ câu trả lời của Trợ lý pháp luật
        with ui.card().classes("w-full answer-card shadow-sm p-4"):
            with ui.row().classes("items-center gap-2 w-full pb-2 border-b border-slate-100 flex-wrap"):
                ui.icon("balance", color="primary", size="sm")
                ui.label("Trợ lý pháp luật Agentic-RAG").classes("font-semibold text-slate-800 text-sm")
                ui.space()
                if turn.response is not None:
                    with ui.row().classes("items-center gap-1.5 flex-wrap"):
                        _status_badges(turn.response)

            # 1. Trạng thái đang xử lý
            if turn.pending:
                pending_pipeline(elapsed_source)
                return

            # 2. Trạng thái lỗi (hiển thị thân thiện kèm gợi ý & nút Thử lại)
            if turn.error is not None:
                with ui.card().classes("w-full bg-red-50/80 border border-red-200 shadow-none p-3 mt-1"):
                    with ui.row().classes("items-start gap-2.5 text-red-800 w-full no-wrap"):
                        ui.icon("error_outline", color="negative", size="sm").classes("mt-0.5")
                        with ui.column().classes("gap-1 grow"):
                            ui.label("Không thể hoàn tất yêu cầu").classes("font-semibold text-sm text-red-900")
                            ui.label(turn.error).classes("text-sm text-red-800")
                            if turn.error_hint:
                                ui.label(turn.error_hint).classes("text-xs text-red-700 font-mono mt-0.5")
                    if on_retry is not None:
                        with ui.row().classes("mt-2 justify-end"):
                            ui.button(
                                "Thử lại câu hỏi này",
                                icon="refresh",
                                on_click=lambda t=turn: on_retry(t),
                            ).props("unelevated dense no-caps color=negative size=sm").classes("px-3")
                return

            # 3. Trạng thái có câu trả lời (hoặc từ chối có chủ đích)
            resp = turn.response
            if resp.refused:
                with ui.card().classes("w-full bg-amber-50 border border-amber-200 shadow-none p-3 mt-1"):
                    with ui.row().classes("items-start gap-2.5"):
                        ui.icon("info", color="warning", size="sm").classes("mt-0.5")
                        with ui.column().classes("gap-1"):
                            ui.label(resp.answer).classes("text-sm font-medium text-amber-900")
                            if resp.refuse_reason:
                                ui.label(f"Chi tiết: {REASONS.get(resp.refuse_reason, resp.refuse_reason)}").classes(
                                    "text-xs text-amber-700"
                                )
            else:
                ui.markdown(answer_markdown(resp.answer)).classes("answer-text w-full pt-1")
                if resp.status == "partial":
                    with ui.row().classes(
                        "items-center gap-2 bg-orange-50 border border-orange-200 rounded-lg px-3 py-2 text-xs text-orange-800"
                    ):
                        ui.icon("warning_amber", color="warning", size="xs")
                        ui.label(
                            "Một số mệnh đề trong câu trả lời chưa được đoạn luật nào hỗ trợ đầy đủ sau bước kiểm chứng; "
                            "hãy đối chiếu nguyên văn Điều luật trước khi áp dụng."
                        )

            # Danh sách chip trích dẫn bấm nhanh để mở ngăn phải
            if resp.citations:
                with ui.row().classes("items-center gap-1.5 flex-wrap pt-1"):
                    ui.label("Đối chiếu nhanh:").classes("text-xs font-medium text-slate-500 mr-1")
                    for c in resp.citations:
                        ui.chip(
                            citation_label(c),
                            icon="gavel",
                            on_click=lambda c=c: on_open(c),
                        ).props("outline clickable color=primary dense").classes("citation-chip")

            # Thanh công cụ: Sao chép, Thử lại, Đánh giá 👍 / 👎
            with ui.row().classes("w-full items-center gap-1 pt-2 pb-1 border-t border-slate-100 text-xs text-slate-500"):
                ui.button(
                    "Sao chép",
                    icon="content_copy",
                    on_click=lambda t=turn: copy_text(
                        format_turn_for_copy(t), "Đã sao chép câu trả lời và căn cứ pháp lý"
                    ),
                ).props("flat dense no-caps size=sm color=slate-600")
                if on_retry is not None:
                    ui.button(
                        "Thử lại",
                        icon="refresh",
                        on_click=lambda t=turn: on_retry(t),
                    ).props("flat dense no-caps size=sm color=slate-600").tooltip("Gửi lại câu hỏi này")
                ui.space()
                ui.label("Đánh giá câu trả lời:").classes("text-xs text-slate-400 mr-1")
                up_color = "positive" if turn.feedback == "up" else "grey-6"
                down_color = "negative" if turn.feedback == "down" else "grey-6"
                ui.button(
                    "Hữu ích",
                    icon="thumb_up",
                    on_click=lambda t=turn: on_feedback(t, "up") if on_feedback else None,
                ).props(f"flat dense no-caps size=sm color={up_color}")
                ui.button(
                    "Chưa chuẩn",
                    icon="thumb_down",
                    on_click=lambda t=turn: on_feedback(t, "down") if on_feedback else None,
                ).props(f"flat dense no-caps size=sm color={down_color}")

            # 3 khu vực mở rộng chi tiết
            with ui.column().classes("w-full gap-0 mt-1"):
                if resp.citations:
                    with ui.expansion(
                        f"Căn cứ pháp luật ({len(resp.citations)})",
                        icon="library_books",
                    ).classes("w-full section"):
                        citation_list(resp.citations, on_open)
                if not resp.refused or resp.event_date:
                    with ui.expansion(
                        "Hiệu lực văn bản" + (f" · mốc {resp.event_date}" if resp.event_date else " · hiện hành"),
                        icon="event_available",
                    ).classes("w-full section"):
                        validity_card(resp)
                with ui.expansion(
                    f"Các bước tác tử · {len(resp.trace)} bước · {resp.total_ms / 1000:.1f} s · "
                    f"{resp.total_llm_calls} lượt LLM",
                    icon="account_tree",
                ).classes("w-full section"):
                    agent_timeline(resp)
