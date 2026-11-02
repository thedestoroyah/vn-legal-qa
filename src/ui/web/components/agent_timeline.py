"""Dòng thời gian và trạng thái xử lý của tác tử: hiển thị cả khi đang chạy (pending) và khi đã hoàn tất (trace)."""
from __future__ import annotations

import json

from nicegui import ui

from src.ui.web.api.schemas import AskResponse, TraceStep
from src.ui.web.config import NODE_ICONS, NODE_LABELS, PIPELINE_PREVIEW_STEPS, REASONS, ROUTES


def step_note(step: TraceStep) -> str:
    """Một dòng tóm tắt dễ đọc cho mỗi bước (cùng cách đọc với src/ui/app.py: step_note)."""
    o = step.output or {}
    node = step.node
    if node == "route":
        route = o.get("route_type")
        note = f"Loại câu hỏi: {ROUTES.get(route, route or 'không xác định')}"
        if o.get("event_date"):
            note += f" · ngày sự việc {o['event_date']}"
        ref = o.get("direct_ref")
        if isinstance(ref, dict) and ref.get("law_id"):
            note += f" · hỏi trực tiếp {ref['law_id']} Điều {ref.get('article')}"
        return note
    if node == "lookup_article":
        evidence = o.get("evidence") or []
        return f"Tìm thấy: {', '.join(evidence)}" if evidence else "Không tìm thấy Điều được hỏi (chuyển sang truy xuất)"
    if node == "retrieve":
        queries = o.get("queries") or []
        extra = f" · truy vấn viết lại: “{queries[-1]}”" if len(queries) > 1 else ""
        return f"Tìm được {len(o.get('evidence') or [])} đoạn luật phù hợp{extra}"
    if node == "grade":
        if o.get("sufficient"):
            return "Đủ căn cứ pháp lý để sinh câu trả lời"
        return "Chưa đủ căn cứ, yêu cầu viết lại truy vấn" if o.get("rewrite") else "Chưa đủ căn cứ, dừng viết lại"
    if node == "generate":
        if o.get("insufficient"):
            return "Mô hình báo không đủ căn cứ để trả lời"
        return f"Sinh câu trả lời thành công (lần {o.get('n_generations', 1)})"
    if node == "verify":
        removed = ", ".join(o.get("removed") or []) or "không"
        return f"Trích dẫn bị gỡ: {removed}" + (" · yêu cầu sinh lại" if o.get("regenerate") else " · mọi trích dẫn hợp lệ")
    if node == "refuse":
        reason = o.get("refuse_reason")
        return f"Lý do: {REASONS.get(reason, reason)}"
    return ""


def _color(step: TraceStep) -> str:
    o = step.output or {}
    if step.node == "refuse" or (step.node == "verify" and o.get("removed")):
        return "orange"
    if step.node == "grade" and not o.get("sufficient"):
        return "orange"
    return "primary"


def pending_pipeline(elapsed_source: object) -> None:
    """Hiển thị trạng thái xử lý trực quan khi Agentic-RAG đang chạy."""
    with ui.column().classes("w-full gap-2.5 py-2 px-1"):
        with ui.row().classes("items-center gap-3 w-full"):
            ui.spinner(size="md", color="primary")
            with ui.column().classes("gap-0"):
                ui.label("Tác tử Agentic-RAG đang xử lý câu hỏi...").classes(
                    "text-sm font-semibold text-slate-700"
                )
                ui.label(
                    "Đang phân tích câu hỏi, truy xuất BM25 + Vector, chấm bằng chứng và kiểm chứng trích dẫn"
                ).classes("text-xs text-slate-500")
            ui.space()
            ui.badge().bind_text_from(
                elapsed_source, "elapsed", backward=lambda s: f"⏱ {s:.1f} s"
            ).props("color=indigo-1 text-color=indigo-9").classes("font-mono text-xs px-2.5 py-1")

        with ui.row().classes("w-full items-center gap-1.5 flex-wrap mt-1"):
            for idx, (icon, label) in enumerate(PIPELINE_PREVIEW_STEPS):
                if idx > 0:
                    ui.icon("east", size="xs").classes("text-slate-300")
                with ui.row().classes(
                    "items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200 agent-pulse"
                ):
                    ui.icon(icon, size="xs", color="primary")
                    ui.label(label).classes("text-xs font-medium text-slate-600")


def agent_timeline(resp: AskResponse) -> None:
    if not resp.trace:
        ui.label("Máy chủ không trả về các bước xử lý.").classes("text-sm text-slate-500")
        return

    # Thanh tóm tắt luồng chạy (Pipeline Stepper Bar)
    with ui.card().classes("w-full bg-slate-50 border border-slate-200 shadow-none p-2.5 mb-2"):
        with ui.row().classes("items-center justify-between w-full mb-1.5 flex-wrap gap-2"):
            ui.label("Luồng thực thi thực tế của tác tử:").classes("text-xs font-semibold text-slate-600")
            with ui.row().classes("items-center gap-2 text-xs text-slate-500"):
                ui.badge(f"Tổng: {resp.total_ms / 1000:.2f} s", color="blue-grey-1", text_color="blue-grey-9").classes("font-mono")
                ui.badge(f"{resp.total_llm_calls} lượt gọi LLM", color="indigo-1", text_color="indigo-9")
        with ui.row().classes("items-center gap-1.5 flex-wrap"):
            for idx, step in enumerate(resp.trace):
                if idx > 0:
                    ui.icon("chevron_right", size="xs").classes("text-slate-400")
                is_warn = _color(step) == "orange"
                bg = "bg-amber-50 border-amber-300 text-amber-900" if is_warn else "bg-white border-slate-200 text-slate-700"
                with ui.row().classes(f"items-center gap-1 px-2.5 py-1 rounded-lg border text-xs {bg}"):
                    ui.icon(NODE_ICONS.get(step.node, "check_circle"), size="xs", color="orange" if is_warn else "primary")
                    ui.label(NODE_LABELS.get(step.node, step.node)).classes("font-medium")
                    ui.label(f"({step.ms}ms)").classes("text-[11px] text-slate-400 font-mono")

    # Timeline chi tiết từng bước
    with ui.timeline(side="right").classes("w-full").props("dense layout=dense"):
        for step in resp.trace:
            with ui.timeline_entry(
                title=NODE_LABELS.get(step.node, step.node),
                subtitle=f"Node: {step.node} · Thời gian: {step.ms} ms · Gọi LLM: {step.llm_calls} lượt",
                icon=NODE_ICONS.get(step.node, "radio_button_checked"),
                color=_color(step),
            ):
                ui.label(step_note(step)).classes("text-sm text-slate-700 font-medium")
                if step.output:
                    with ui.expansion("Xem dữ liệu JSON của bước", icon="data_object").props("dense").classes(
                        "text-xs w-full mt-1"
                    ):
                        ui.code(json.dumps(step.output, ensure_ascii=False, indent=2), language="json").classes(
                            "w-full text-xs"
                        )
