"""Thanh bên (Sidebar): chia thành Header cố định, Vùng cuộn dọc độc lập (.sidebar-scroll) và Footer cố định."""
from __future__ import annotations

from collections.abc import Awaitable, Callable

from nicegui import ui

from src.ui.web.config import AGENT_CONFIGS, APP_SUBTITLE, APP_TITLE, DISCLAIMER, LAWS_CATALOG


def brand(on_close_sidebar: Callable[[], None] | None = None) -> None:
    with ui.row().classes("items-center justify-between w-full no-wrap gap-2"):
        with ui.row().classes("items-center gap-2.5 min-w-0 no-wrap"):
            with ui.element("div").classes(
                "p-1.5 rounded-lg bg-blue-900 text-white flex items-center justify-center shrink-0 shadow-sm"
            ):
                ui.icon("balance", size="1.25rem")
            with ui.column().classes("gap-0 min-w-0"):
                ui.label(APP_TITLE).classes("text-sm font-bold text-slate-800 leading-tight truncate")
                ui.label(APP_SUBTITLE).classes("text-[11px] text-slate-500 font-medium truncate")
        if on_close_sidebar is not None:
            ui.button(icon="chevron_left", on_click=on_close_sidebar).props(
                "id=sidebar-close-btn flat round dense size=sm color=slate-600"
            ).tooltip("Thu gọn thanh bên")


def new_chat_actions(
    state,
    on_new: Callable[[], None],
    on_clear_all: Callable[[], None] | None = None,
    on_export: Callable[[], None] | None = None,
) -> None:
    with ui.row().classes("w-full gap-1.5 no-wrap"):
        btn = ui.button("Hội thoại mới", icon="add_comment", on_click=on_new).props(
            "unelevated dense no-caps color=primary"
        ).classes("grow py-1 text-xs font-semibold")
        if getattr(state, "busy", False):
            btn.disable()
        if on_export is not None and state.current.turns:
            ui.button(icon="ios_share", on_click=on_export).props("outline dense size=sm color=primary").tooltip(
                "Sao chép toàn bộ hội thoại (.md)"
            )
        if on_clear_all is not None and (len(state.conversations) > 1 or state.current.turns):
            ui.button(icon="delete_sweep", on_click=on_clear_all).props("outline dense size=sm color=negative").tooltip(
                "Xóa toàn bộ lịch sử phiên"
            )


def conversations(
    state,
    on_new: Callable[[], None],
    on_select: Callable[[int], None],
    on_delete: Callable[[int], None],
    on_clear_all: Callable[[], None] | None = None,
    on_export: Callable[[], None] | None = None,
    include_top_buttons: bool = True,
) -> None:
    if include_top_buttons:
        new_chat_actions(state, on_new, on_clear_all, on_export)

    history_open = getattr(state, "history_expanded", True)
    with ui.expansion(
        f"Lịch sử trong phiên ({len(state.conversations)})",
        icon="forum",
        value=history_open,
    ).props("dense header-class='text-xs font-semibold text-slate-700 px-1'").classes(
        "session-history w-full max-w-full bg-white border border-slate-200 rounded-lg px-1.5 py-0.5 min-w-0"
    ) as exp:
        exp.on_value_change(lambda e: setattr(state, "history_expanded", bool(e.value)))
        with ui.column().classes("session-history-list w-full max-w-full no-wrap gap-1 py-1 min-w-0"):
            for i, conv in enumerate(state.conversations):
                active = i == state.current_index
                with ui.row().classes(
                    "w-full max-w-full items-center no-wrap conv-item" + (" conv-active" if active else "")
                ):
                    ui.icon(
                        "chat_bubble" if active else "chat_bubble_outline",
                        size="xs",
                        color="primary" if active else "grey-6",
                    ).classes("mr-1.5 shrink-0")
                    with ui.column().classes("gap-0 flex-1 cursor-pointer min-w-0 overflow-hidden").on(
                        "click", lambda _, idx=i: on_select(idx)
                    ):
                        ui.label(conv.title).classes(
                            "w-full text-xs truncate " + ("font-semibold text-blue-950" if active else "text-slate-700")
                        )
                        ui.label(f"{len(conv.turns)} lượt hỏi · {conv.updated_at:%H:%M}").classes(
                            "w-full text-[10px] text-slate-400 truncate"
                        )
                    if len(state.conversations) > 1:
                        ui.button(icon="close").props(
                            "flat round dense size=xs color=grey-7 @click.stop"
                        ).tooltip("Xóa hội thoại này").on(
                            "click", lambda _, idx=i: on_delete(idx)
                        )


def config_select(state) -> None:
    ui.select(AGENT_CONFIGS, label="Cấu hình tác tử (Ablation)").bind_value(state, "config").props(
        "dense outlined options-dense bg-color=white"
    ).classes("w-full text-xs")


def api_status(state, on_check: Callable[[], Awaitable[None]]) -> None:
    """Card trạng thái API gọn gàng, không chiếm nhiều diện tích dọc."""
    border_cls = (
        "border-emerald-200 bg-emerald-50/50"
        if state.api_ok is True
        else ("border-red-200 bg-red-50/60" if state.api_ok is False else "border-slate-200 bg-white")
    )
    with ui.card().classes(f"w-full shadow-none border p-2.5 rounded-lg min-w-0 {border_cls}"):
        with ui.row().classes("items-center justify-between w-full no-wrap gap-1"):
            with ui.row().classes("items-center gap-1.5 min-w-0 no-wrap"):
                ui.icon(
                    "check_circle" if state.api_ok is True else ("error" if state.api_ok is False else "sync"),
                    size="xs",
                    color="positive" if state.api_ok is True else ("negative" if state.api_ok is False else "primary"),
                )
                ui.label("API:").classes("text-xs font-semibold text-slate-700 shrink-0")
                if state.api_ok is None:
                    ui.label("Đang kiểm tra...").classes("text-xs text-slate-500 truncate")
                elif state.api_ok:
                    ui.badge("Đã kết nối", color="positive").classes("text-[10px] px-1.5 py-0")
                else:
                    ui.badge("Mất kết nối", color="negative").classes("text-[10px] px-1.5 py-0")
            ui.button(icon="refresh", on_click=on_check).props(
                "flat round dense size=xs color=primary"
            ).tooltip("Kiểm tra lại kết nối API")

        with ui.row().classes("items-center justify-between w-full gap-1 mt-1 text-[11px] text-slate-500 min-w-0"):
            if state.api_ok and state.api_model:
                ui.label(f"Model: {state.api_model}").classes("font-mono text-[11px] text-indigo-900 truncate")
            elif state.api_ok is False and state.api_error:
                ui.label(state.api_error).classes("text-[11px] text-red-700 leading-tight")
            ui.label(state.api_url).classes("text-[10px] text-slate-400 font-mono truncate max-w-full")


def scope() -> None:
    """Danh sách 5 văn bản pháp luật có thể mở rộng/thu gọn và hiển thị đầy đủ khi cuộn."""
    with ui.expansion("Phạm vi 5 văn bản pháp luật", icon="inventory_2", value=True).props(
        "dense header-class='text-xs font-semibold text-slate-600 px-1'"
    ).classes("w-full bg-white border border-slate-200 rounded-lg px-1.5 py-0.5 min-w-0"):
        with ui.column().classes("w-full gap-1.5 py-1 min-w-0"):
            for law in LAWS_CATALOG.values():
                active = law.get("status") == "Còn hiệu lực"
                with ui.column().classes("w-full gap-0.5 p-1.5 rounded bg-slate-50 border border-slate-100 min-w-0"):
                    with ui.row().classes("items-center justify-between w-full no-wrap gap-1 min-w-0"):
                        with ui.row().classes("items-center gap-1.5 min-w-0 no-wrap"):
                            ui.icon("circle", size="0.45rem", color="positive" if active else "negative").classes(
                                "shrink-0"
                            )
                            ui.label(f"{law.get('document')}").classes(
                                "text-xs font-medium text-slate-800 leading-snug break-words"
                            )
                    with ui.row().classes("items-center justify-between w-full gap-1 pl-3 text-[10px] text-slate-500"):
                        ui.label(f"Số: {law.get('number', '—')}").classes("font-mono")
                        ui.badge(
                            law.get("status", ""),
                            color="emerald-1" if active else "amber-1",
                            text_color="emerald-9" if active else "amber-9",
                        ).classes("text-[10px] px-1.5 py-0")


def footer_disclaimer() -> None:
    ui.label(DISCLAIMER).classes("text-[11px] text-slate-400 leading-snug")
