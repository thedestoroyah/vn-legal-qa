"""Thẻ căn cứ pháp luật (citations) và bảng xem toàn văn Điều có tô sáng Khoản được trích."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
import json

from nicegui import ui

from src.ui.article_view import clause_number, split_clauses
from src.ui.web.api.client import parse_chunk_id
from src.ui.web.api.schemas import ArticleResponse, CitationItem
from src.ui.web.config import LAWS_CATALOG


def citation_label(c: CitationItem) -> str:
    return f"{c.document} – {c.article}" + (f", {c.clause}" if c.clause else "")


def law_of(chunk_id: str) -> dict:
    """Mục laws.json của văn bản chứa chunk_id ({} nếu không có)."""
    parsed = parse_chunk_id(chunk_id)
    return LAWS_CATALOG.get(parsed[0], {}) if parsed else {}


def copy_text(text: str, label: str = "Đã sao chép vào bộ nhớ tạm") -> None:
    """Sao chép chuỗi vào clipboard trình duyệt và hiện thông báo."""
    payload = json.dumps(text, ensure_ascii=False)
    ui.run_javascript(f"navigator.clipboard && navigator.clipboard.writeText({payload});")
    ui.notify(label, type="positive", position="bottom-right", timeout=1800)


def citation_list(citations: list[CitationItem], on_open: Callable[[CitationItem], Awaitable[None]]) -> None:
    """Danh sách căn cứ: mỗi căn cứ hiển thị số thứ tự, thông tin văn bản, đoạn trích, nút xem toàn văn & sao chép."""
    with ui.column().classes("w-full gap-2.5 py-1"):
        for idx, c in enumerate(citations, start=1):
            law = law_of(c.chunk_id)
            status = law.get("status")
            with ui.expansion(f"{idx}. {citation_label(c)}", icon="gavel", value=(idx == 1)).classes(
                "w-full citation-card"
            ).props("dense"):
                with ui.column().classes("w-full gap-2 pt-1 pb-2 px-1"):
                    with ui.row().classes("items-center gap-2 flex-wrap text-xs text-slate-500"):
                        ui.badge(c.chunk_id, color="indigo-1", text_color="indigo-9").classes("font-mono px-2 py-0.5")
                        if law.get("number"):
                            ui.label(f"Số hiệu: {law['number']}").classes("font-medium text-slate-600")
                        if status:
                            ui.badge(
                                status,
                                color="positive" if status == "Còn hiệu lực" else "negative",
                            ).props("outline")
                    ui.label(c.content or "(API không trả nội dung đoạn trích)").classes(
                        "citation-excerpt whitespace-pre-line text-sm text-slate-700"
                    )
                    with ui.row().classes("items-center gap-2 mt-1 flex-wrap"):
                        ui.button(
                            "Xem toàn văn Điều",
                            icon="menu_book",
                            on_click=lambda c=c: on_open(c),
                        ).props("unelevated dense no-caps color=primary size=sm").classes("px-3")
                        ui.button(
                            "Sao chép trích dẫn",
                            icon="content_copy",
                            on_click=lambda c=c: copy_text(
                                f"{citation_label(c)} [{c.chunk_id}]:\n{c.content}",
                                f"Đã sao chép {c.chunk_id}",
                            ),
                        ).props("outline dense no-caps color=primary size=sm").classes("px-2.5")
                        if law.get("source"):
                            ui.link("Nguồn VBPL ↗", law["source"], new_tab=True).classes(
                                "text-xs font-medium text-blue-800 hover:underline ml-auto self-center"
                            )


def article_panel(
    citation: CitationItem | None,
    article: ArticleResponse | None,
    loading: bool,
    recent_citations: list[CitationItem] | None = None,
    on_open: Callable[[CitationItem], Awaitable[None]] | None = None,
) -> None:
    """Nội dung ngăn phải: toàn văn Điều từ GET /api/article, Khoản được trích tô sáng & cuộn tự động."""
    if citation is None:
        with ui.column().classes("w-full items-center text-center text-slate-500 gap-2 mt-8 px-3"):
            ui.icon("menu_book", size="2.8rem", color="primary").classes("opacity-80")
            ui.label("Chưa chọn điều luật").classes("text-base font-semibold text-slate-700")
            ui.label("Bấm vào thẻ trích dẫn trong câu trả lời để đối chiếu nguyên văn toàn Điều luật và các Khoản liên quan.").classes(
                "text-xs text-slate-500 leading-relaxed"
            )
            if recent_citations and on_open is not None:
                ui.separator().classes("my-2")
                ui.label("Trích dẫn trong cuộc hội thoại hiện tại:").classes(
                    "text-xs font-semibold text-slate-600 self-start"
                )
                with ui.column().classes("w-full gap-1.5"):
                    for c in recent_citations:
                        with ui.card().classes(
                            "w-full p-2.5 cursor-pointer sample-card text-left"
                        ).on("click", lambda c=c: on_open(c)):
                            with ui.row().classes("items-center justify-between w-full no-wrap"):
                                ui.label(citation_label(c)).classes("text-xs font-semibold text-primary truncate")
                                ui.icon("chevron_right", size="xs", color="primary")
                            ui.label(c.chunk_id).classes("text-[11px] font-mono text-slate-400")
        return

    if loading:
        with ui.column().classes("w-full items-center justify-center gap-3 mt-12 py-8"):
            ui.spinner(size="lg", color="primary")
            ui.label(f"Đang tải nguyên văn {citation.chunk_id}...").classes("text-sm text-slate-600 font-medium")
        return

    if article is None:
        with ui.card().classes("w-full bg-amber-50 border border-amber-200 shadow-none p-3 mt-2"):
            with ui.row().classes("items-center gap-2 text-amber-900"):
                ui.icon("warning_amber", color="warning")
                ui.label(f"Không tìm thấy toàn văn của {citation.chunk_id}").classes("font-semibold text-sm")
            ui.label("Hiển thị đoạn trích lưu trong câu trả lời:").classes("text-xs text-amber-700 mt-1")
            ui.label(citation.content or "(Không có nội dung)").classes(
                "whitespace-pre-line text-sm text-slate-800 bg-white p-2.5 rounded border border-amber-100 mt-1"
            )
        return

    law = law_of(article.chunk_id)
    status = article.status or law.get("status")
    number = article.number or law.get("number")

    with ui.card().classes("w-full bg-slate-50 border border-slate-200 shadow-none p-3 mt-1"):
        with ui.row().classes("items-center justify-between w-full gap-2 flex-wrap"):
            ui.badge(article.chunk_id, color="indigo-1", text_color="indigo-9").classes("font-mono text-xs")
            if status:
                ui.badge(
                    status,
                    color="positive" if status == "Còn hiệu lực" else "negative",
                )
        ui.label(f"{article.document} – {article.article}").classes("text-base font-bold text-slate-800 mt-1")
        if article.article_title:
            ui.label(article.article_title).classes("text-sm font-medium text-primary")
        with ui.row().classes("items-center gap-3 text-xs text-slate-500 mt-1 flex-wrap"):
            if number:
                ui.label(f"Số hiệu: {number}")
            if law.get("effective_date"):
                ui.label(f"Hiệu lực: {law['effective_date']}")
            if law.get("expiry_date"):
                ui.label(f"Hết hiệu lực: {law['expiry_date']}")
        with ui.row().classes("items-center gap-2 mt-2 pt-2 border-t border-slate-200 w-full"):
            ui.button(
                "Sao chép toàn văn",
                icon="content_copy",
                on_click=lambda: copy_text(
                    f"{article.document} - {article.article}"
                    + (f": {article.article_title}\n" if article.article_title else "\n")
                    + article.content,
                    f"Đã sao chép toàn văn {article.article}",
                ),
            ).props("outline dense no-caps color=primary size=sm").classes("px-2.5")
            if law.get("source"):
                ui.link("Mở văn bản gốc trên vbpl.vn ↗", law["source"], new_tab=True).classes(
                    "text-xs font-medium text-blue-800 hover:underline ml-auto"
                )

    target = clause_number(citation.clause)
    clauses = split_clauses(article.content)
    with ui.column().classes("w-full gap-2.5 mt-3 pb-6"):
        for num, text in clauses:
            if num is not None and num == target:
                with ui.column().classes("w-full clause-highlight gap-1"):
                    with ui.row().classes("items-center justify-between w-full"):
                        ui.badge(f"Đang trích dẫn · Khoản {num}", color="positive").classes("text-[11px]")
                        ui.button(
                            icon="content_copy",
                            on_click=lambda t=text, n=num: copy_text(t, f"Đã sao chép Khoản {n}"),
                        ).props("flat round dense size=xs color=positive").tooltip("Sao chép khoản này")
                    ui.label(text).classes("whitespace-pre-line text-sm leading-relaxed")
            else:
                with ui.column().classes("w-full clause-normal gap-1"):
                    if num is not None:
                        ui.label(f"Khoản {num}").classes("text-[11px] font-semibold text-slate-400 uppercase")
                    ui.label(text).classes("whitespace-pre-line text-sm text-slate-700 leading-relaxed")
