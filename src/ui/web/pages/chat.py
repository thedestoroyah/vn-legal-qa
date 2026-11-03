"""Trang hỏi đáp: bố cục Flexbox toàn màn hình (100dvh, overflow: hidden) gồm 3 vùng độc lập:
1. SIDEBAR (Header cố định + Vùng cuộn độc lập + Footer cố định)
2. CHAT AREA (Header + Vùng tin nhắn cuộn độc lập + Composer cố định ở đáy)
3. LEGAL PANEL (Header + Nội dung điều luật cuộn độc lập, đóng/mở linh hoạt)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import time

from nicegui import ui

from src.ui.web.api.client import ApiClientError, LegalQAApiClient
from src.ui.web.api.schemas import ArticleResponse, CitationItem
from src.ui.web.components import sidebar
from src.ui.web.components.chat_message import Turn, format_turn_for_copy, render_turn
from src.ui.web.components.citation_card import article_panel, copy_text
from src.ui.web.config import DISCLAIMER, MAX_QUESTION, SAMPLE_QUESTIONS, STATIC_DIR

SAMPLE_ICONS: dict[str, str] = {
    "Tra cứu trực tiếp": "menu_book",
    "Tình huống thực tế": "gavel",
    "Hiệu lực theo thời gian": "history",
    "Ngoài phạm vi": "shield",
}


@dataclass
class Conversation:
    turns: list[Turn] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def title(self) -> str:
        if not self.turns:
            return "Hội thoại mới"
        q = self.turns[0].question
        return q if len(q) <= 42 else q[:42] + "…"

    @property
    def all_citations(self) -> list[CitationItem]:
        """Tất cả trích dẫn trong cuộc hội thoại (bỏ trùng theo chunk_id)."""
        seen: set[str] = set()
        items: list[CitationItem] = []
        for t in reversed(self.turns):
            if t.response:
                for c in t.response.citations:
                    if c.chunk_id not in seen:
                        seen.add(c.chunk_id)
                        items.append(c)
        return items


@dataclass
class PageState:
    """Trạng thái của một tab trình duyệt (mỗi tab một bản, không chia sẻ giữa người dùng)."""

    api_url: str
    conversations: list[Conversation] = field(default_factory=lambda: [Conversation()])
    current_index: int = 0
    config: str = "full"
    draft: str = ""
    busy: bool = False
    started: float = 0.0
    elapsed: float = 0.0
    api_ok: bool | None = None
    api_model: str = ""
    api_error: str = ""
    api_hint: str = ""
    sidebar_open: bool = True
    history_expanded: bool = True
    panel_open: bool = False
    selected: CitationItem | None = None
    article: ArticleResponse | None = None
    article_loading: bool = False

    @property
    def current(self) -> Conversation:
        return self.conversations[self.current_index]

    @property
    def can_send(self) -> bool:
        return (not self.busy) and bool((self.draft or "").strip()) and len((self.draft or "").strip()) <= MAX_QUESTION


async def chat_page(api: LegalQAApiClient) -> None:
    state = PageState(api_url=api.base_url)
    ui.add_css((STATIC_DIR / "styles.css").read_text(encoding="utf-8"))
    ui.colors(primary="#1e3a8a")
    ui.page_title("Hỏi đáp pháp luật Việt Nam · Agentic-RAG")

    # ---------- Điều khiển đóng/mở Sidebar & Legal Panel ----------
    def sync_panels() -> None:
        if state.sidebar_open:
            sidebar_el.classes(remove="sidebar-closed")
        else:
            sidebar_el.classes(add="sidebar-closed")

        if state.panel_open:
            legal_panel_el.classes(remove="panel-closed")
        else:
            legal_panel_el.classes(add="panel-closed")

    def toggle_sidebar() -> None:
        state.sidebar_open = not state.sidebar_open
        sync_panels()

    def toggle_panel() -> None:
        state.panel_open = not state.panel_open
        sync_panels()

    def close_panel() -> None:
        state.panel_open = False
        sync_panels()

    # ---------- Cuộn thông minh vùng Chat Messages ----------
    def scroll_messages(force: bool = False) -> None:
        try:
            js_force = "true" if force else "false"
            ui.run_javascript(
                f"""
                setTimeout(() => {{
                    const box = document.getElementById('chat-messages');
                    if (!box) return;
                    if ({js_force} || window.__chatNearBottom !== false) {{
                        box.scrollTo({{ top: box.scrollHeight, behavior: 'smooth' }});
                        window.__chatNearBottom = true;
                    }}
                }}, 60);
                """
            )
        except Exception:
            pass

    # ---------- Cuộn danh sách lịch sử tới mục đang chọn ----------
    def scroll_history_to_active() -> None:
        try:
            ui.run_javascript(
                """
                setTimeout(() => {
                    const active = document.querySelector('.session-history-list .conv-item.conv-active');
                    if (active) {
                        active.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
                    }
                }, 80);
                """
            )
        except Exception:
            pass

    def sync_composer_state() -> None:
        text = (box.value or "").strip()
        state.draft = box.value or ""
        char_count_label.set_text(f"{len(state.draft)}/{MAX_QUESTION}")
        if state.busy:
            send_btn.props("loading")
            send_btn.disable()
            clear_btn.disable()
            box.disable()
        else:
            send_btn.props(remove="loading")
            box.enable()
            if text and len(text) <= MAX_QUESTION:
                send_btn.enable()
            else:
                send_btn.disable()
            if state.draft:
                clear_btn.enable()
            else:
                clear_btn.disable()

    # ---------- Hành động API & Hội thoại ----------
    async def check_api() -> None:
        state.api_ok = None
        sidebar_api_view.refresh()
        banner_view.refresh()
        try:
            health = await api.health()
            state.api_ok, state.api_model, state.api_error, state.api_hint = True, health.model, "", ""
        except ApiClientError as e:
            state.api_ok, state.api_error, state.api_hint = False, e.message, e.hint
        sidebar_api_view.refresh()
        banner_view.refresh()

    async def open_article(c: CitationItem) -> None:
        state.selected, state.article, state.article_loading = c, None, True
        state.panel_open = True
        sync_panels()
        article_view.refresh()
        art = await api.article(c.chunk_id)
        if state.selected is c:
            state.article, state.article_loading = art, False
            article_view.refresh()
            ui.run_javascript(
                """
                setTimeout(() => {
                    const panel = document.getElementById('legal-panel-body');
                    const el = panel ? panel.querySelector('.clause-highlight') : null;
                    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 100);
                """
            )

    async def _execute_turn(turn: Turn) -> None:
        turn.response = None
        turn.error = None
        turn.error_hint = ""
        state.current.updated_at = datetime.now()
        state.busy, state.started, state.elapsed = True, time.monotonic(), 0.0
        sync_composer_state()
        chat_view.refresh()
        sidebar_actions_view.refresh()
        sidebar_history_view.refresh()
        scroll_messages(force=True)
        try:
            turn.response = await api.ask(turn.question, turn.config)
            if state.api_ok is not True:
                state.api_ok, state.api_error, state.api_hint = True, "", ""
                banner_view.refresh()
        except ApiClientError as e:
            turn.error = e.message
            turn.error_hint = e.hint
            if e.kind == "network":
                state.api_ok, state.api_error, state.api_hint = False, e.message, e.hint
                banner_view.refresh()
        finally:
            state.busy = False
            state.current.updated_at = datetime.now()
            sync_composer_state()
            chat_view.refresh()
            sidebar_actions_view.refresh()
            sidebar_history_view.refresh()
            article_view.refresh()
            scroll_messages(force=False)

    async def send() -> None:
        if state.busy:
            return
        question = (box.value or "").strip()
        if not question:
            return
        if len(question) > MAX_QUESTION:
            ui.notify(f"Câu hỏi dài {len(question)} ký tự, tối đa {MAX_QUESTION}.", type="warning", position="top")
            return
        turn = Turn(question=question, config=state.config)
        state.current.turns.append(turn)
        box.value = ""
        state.draft = ""
        await _execute_turn(turn)

    async def retry_turn(turn: Turn) -> None:
        if state.busy:
            return
        await _execute_turn(turn)

    def set_feedback(turn: Turn, value: str) -> None:
        turn.feedback = None if turn.feedback == value else value
        chat_view.refresh()
        if turn.feedback == "up":
            ui.notify("Cảm ơn phản hồi tích cực của bạn!", type="positive", position="bottom-right", timeout=1500)
        elif turn.feedback == "down":
            ui.notify("Đã ghi nhận đánh giá để cải thiện chất lượng câu trả lời.", type="info", position="bottom-right", timeout=1800)

    def new_conversation() -> None:
        if state.current.turns:
            state.conversations.append(Conversation())
        state.current_index = len(state.conversations) - 1
        state.selected = state.article = None
        chat_view.refresh()
        sidebar_actions_view.refresh()
        sidebar_history_view.refresh()
        article_view.refresh()
        scroll_history_to_active()

    def select_conversation(i: int) -> None:
        state.current_index = i
        chat_view.refresh()
        sidebar_actions_view.refresh()
        sidebar_history_view.refresh()
        article_view.refresh()
        scroll_messages(force=True)
        scroll_history_to_active()

    def delete_conversation(i: int) -> None:
        if len(state.conversations) <= 1:
            return
        state.conversations.pop(i)
        state.current_index = min(
            state.current_index if state.current_index < i else state.current_index - 1,
            len(state.conversations) - 1,
        )
        chat_view.refresh()
        sidebar_actions_view.refresh()
        sidebar_history_view.refresh()
        article_view.refresh()

    def clear_all_conversations() -> None:
        state.conversations = [Conversation()]
        state.current_index = 0
        state.selected = state.article = None
        chat_view.refresh()
        sidebar_actions_view.refresh()
        sidebar_history_view.refresh()
        article_view.refresh()
        ui.notify("Đã xóa toàn bộ lịch sử hội thoại trong phiên.", type="info", position="bottom-right")

    def export_conversation_md() -> None:
        if not state.current.turns:
            return
        blocks = [f"# {state.current.title}\n"]
        for idx, t in enumerate(state.current.turns, start=1):
            blocks.append(f"## Lượt {idx}\n{format_turn_for_copy(t)}\n")
        copy_text("\n".join(blocks), "Đã sao chép toàn bộ hội thoại (Markdown) vào bộ nhớ tạm")

    def use_sample(q: str) -> None:
        box.value = q
        state.draft = q
        sync_composer_state()
        box.run_method("focus")

    def clear_input() -> None:
        if state.busy:
            return
        box.value = ""
        state.draft = ""
        sync_composer_state()
        box.run_method("focus")

    def tick() -> None:
        if state.busy:
            state.elapsed = time.monotonic() - state.started

    # ==========================================================================
    # BỐ CỤC TỔNG THỂ: APP SHELL (100dvh, overflow: hidden)
    # ==========================================================================
    with ui.element("div").classes("app-shell"):
        # ----------------------------------------------------------------------
        # 1. SIDEBAR BÊN TRÁI (Header + Actions + Scroll Area + Footer)
        # ----------------------------------------------------------------------
        with ui.element("aside").classes("app-sidebar sidebar") as sidebar_el:
            with ui.element("div").classes("sidebar-header"):
                sidebar.brand(on_close_sidebar=toggle_sidebar)

            with ui.element("div").classes("sidebar-actions"):
                @ui.refreshable
                def sidebar_actions_view() -> None:
                    sidebar.new_chat_actions(
                        state,
                        new_conversation,
                        on_clear_all=clear_all_conversations,
                        on_export=export_conversation_md,
                    )

                sidebar_actions_view()

            with ui.element("div").classes("sidebar-content sidebar-scroll"):
                @ui.refreshable
                def sidebar_history_view() -> None:
                    sidebar.conversations(
                        state,
                        new_conversation,
                        select_conversation,
                        delete_conversation,
                        include_top_buttons=False,
                    )

                sidebar_history_view()

                with ui.element("div").classes("sidebar-section"):
                    sidebar.config_select(state)

                @ui.refreshable
                def sidebar_api_view() -> None:
                    sidebar.api_status(state, check_api)

                sidebar_api_view()

                with ui.element("div").classes("sidebar-section"):
                    sidebar.scope()

            with ui.element("div").classes("sidebar-footer"):
                sidebar.footer_disclaimer()

        # ----------------------------------------------------------------------
        # 2. MAIN CONTENT (CHAT AREA + LEGAL PANEL)
        # ----------------------------------------------------------------------
        with ui.element("main").classes("app-main"):
            # --- 2A. CHAT AREA (Header + Messages Scroll + Composer) ---
            with ui.element("section").classes("chat-area"):
                # Chat Header (flex-shrink: 0)
                with ui.element("div").classes("chat-header"):
                    ui.button(icon="menu", on_click=toggle_sidebar).props(
                        "id=sidebar-toggle-btn flat round dense color=primary"
                    ).tooltip("Đóng/mở thanh bên")
                    ui.icon("balance", color="primary", size="sm")
                    ui.label("Hỏi đáp pháp luật Việt Nam").classes(
                        "text-sm md:text-base font-bold text-slate-800 truncate"
                    )
                    ui.badge("Agentic-RAG", color="indigo-1", text_color="indigo-9").classes(
                        "text-[11px] hidden sm:inline-flex"
                    )
                    ui.space()
                    ui.button("Toàn văn Điều luật", icon="menu_book", on_click=toggle_panel).props(
                        "outline dense no-caps color=primary size=sm"
                    ).classes("px-2.5")

                # Chat Messages (flex: 1, min-height: 0, overflow-y: auto)
                with ui.element("div").props("id=chat-messages").classes("chat-messages"):
                    with ui.element("div").classes("chat-messages-inner"):
                        @ui.refreshable
                        def banner_view() -> None:
                            if state.api_ok is False:
                                with ui.card().classes(
                                    "w-full bg-red-50 border border-red-200 shadow-none p-3 turn-animate"
                                ):
                                    with ui.row().classes("items-center justify-between w-full gap-2 flex-wrap"):
                                        with ui.row().classes("items-center gap-2 text-red-900"):
                                            ui.icon("cloud_off", color="negative", size="sm")
                                            with ui.column().classes("gap-0"):
                                                ui.label("Chưa kết nối được máy chủ FastAPI Backend").classes(
                                                    "text-sm font-semibold"
                                                )
                                                ui.label(
                                                    state.api_error
                                                    or f"Không thể kết nối tới {state.api_url}."
                                                ).classes("text-xs text-red-700")
                                        ui.button("Kiểm tra lại kết nối", icon="refresh", on_click=check_api).props(
                                            "unelevated dense no-caps color=negative size=sm"
                                        ).classes("px-3")

                        banner_view()

                        @ui.refreshable
                        def chat_view() -> None:
                            conv = state.current
                            if not conv.turns:
                                with ui.element("div").classes("welcome-wrapper turn-animate"):
                                    with ui.element("div").classes(
                                        "p-3 rounded-2xl bg-blue-50 border border-blue-100 text-blue-900 shadow-sm"
                                    ):
                                        ui.icon("balance", size="2.4rem", color="primary")
                                    ui.label("Hệ thống Hỏi đáp Pháp luật Việt Nam với Agentic-RAG").classes(
                                        "text-lg md:text-xl font-bold text-slate-800"
                                    )
                                    ui.label(
                                        "Tra cứu chính xác Bộ luật Dân sự, Bộ luật Lao động (2012 & 2019), Luật Doanh nghiệp và Luật Thương mại. "
                                        "Mọi câu trả lời đều kèm căn cứ [Điều/Khoản], kiểm tra hiệu lực thời gian và hậu kiểm chống bịa đặt."
                                    ).classes("text-xs md:text-sm text-slate-600 max-w-2xl leading-relaxed")

                                    with ui.row().classes("items-center gap-1.5 flex-wrap justify-center"):
                                        for badge_text in [
                                            "5 văn bản luật chính thức",
                                            "2.275 điều · 5.427 khoản",
                                            "Truy xuất lai BM25 + BGE-M3",
                                            "Kiểm chứng hiệu lực & trích dẫn",
                                        ]:
                                            ui.badge(badge_text, color="slate-100", text_color="slate-700").classes(
                                                "text-[11px] px-2 py-0.5 border border-slate-200"
                                            )

                                    ui.label("Chọn câu hỏi gợi ý để bắt đầu:").classes(
                                        "text-[11px] font-semibold text-slate-500 uppercase tracking-wider mt-2"
                                    )
                                    with ui.element("div").classes("sample-grid"):
                                        for kind, q in SAMPLE_QUESTIONS:
                                            with ui.card().classes("sample-card cursor-pointer p-3 text-left").on(
                                                "click", lambda q=q: use_sample(q)
                                            ):
                                                with ui.row().classes("items-center justify-between w-full mb-1"):
                                                    with ui.row().classes("items-center gap-1.5"):
                                                        ui.icon(
                                                            SAMPLE_ICONS.get(kind, "help_outline"),
                                                            size="xs",
                                                            color="primary",
                                                        )
                                                        ui.label(kind).classes("text-xs font-bold text-primary")
                                                    ui.icon("north_west", size="xs").classes("text-slate-300")
                                                ui.label(q).classes(
                                                    "text-xs md:text-sm text-slate-700 line-clamp-3 leading-snug"
                                                )
                                return

                            with ui.column().classes("w-full gap-4"):
                                for turn in conv.turns:
                                    render_turn(
                                        turn,
                                        open_article,
                                        state,
                                        on_retry=retry_turn,
                                        on_feedback=set_feedback,
                                    )

                        chat_view()

                # Chat Composer (flex-shrink: 0, nằm cố định ở đáy CHAT AREA)
                with ui.element("div").classes("chat-composer"):
                    with ui.element("div").classes("composer-inner"):
                        with ui.card().classes("w-full input-card"):
                            box = (
                                ui.textarea(
                                    placeholder="Nhập câu hỏi pháp luật... (Enter để gửi, Shift+Enter để xuống dòng)",
                                    on_change=lambda _: sync_composer_state(),
                                )
                                .props(f"id=composer-box autogrow borderless maxlength={MAX_QUESTION}")
                                .classes("w-full composer-textarea text-sm")
                            )
                            box.on("keydown.ctrl.enter", send)
                            with ui.row().classes("w-full items-center gap-2 pt-1 border-t border-slate-100"):
                                ui.label().bind_text_from(
                                    state,
                                    "busy",
                                    backward=lambda b: "⏳ Đang phân tích và tra cứu văn bản pháp luật..."
                                    if b
                                    else "Enter: gửi · Shift+Enter: xuống dòng",
                                ).classes("text-[11px] text-slate-400 hidden sm:block")
                                ui.space()
                                char_count_label = ui.label(f"0/{MAX_QUESTION}").classes(
                                    "text-[11px] font-mono text-slate-400 mr-1"
                                )
                                clear_btn = (
                                    ui.button("Xóa", icon="backspace", on_click=clear_input)
                                    .props("id=composer-clear-btn flat no-caps dense size=sm color=slate-600")
                                )
                                send_btn = (
                                    ui.button("Gửi câu hỏi", icon="send", on_click=send)
                                    .props("id=composer-send-btn unelevated no-caps dense color=primary size=sm")
                                    .classes("px-3.5 py-1")
                                )
                        ui.label(DISCLAIMER).classes("text-[10px] text-slate-400 text-center w-full mt-1 block")

            # --- 2B. PANEL NGUYÊN VĂN ĐIỀU LUẬT BÊN PHẢI (100dvh, đóng/mở độc lập) ---
            with ui.element("aside").classes("legal-panel panel-closed") as legal_panel_el:
                with ui.element("div").classes("legal-panel-header"):
                    ui.icon("menu_book", color="primary", size="xs")
                    ui.label("Nguyên văn điều luật").classes(
                        "text-xs font-bold text-slate-700 uppercase tracking-wider"
                    )
                    ui.space()
                    ui.button(icon="close", on_click=close_panel).props(
                        "flat round dense size=sm color=slate-600"
                    ).tooltip("Đóng panel điều luật")

                with ui.element("div").props("id=legal-panel-body").classes("legal-panel-body"):
                    @ui.refreshable
                    def article_view() -> None:
                        article_panel(
                            state.selected,
                            state.article,
                            state.article_loading,
                            recent_citations=state.current.all_citations,
                            on_open=open_article,
                        )

                    article_view()

    # Khởi tạo trạng thái nút Composer và gắn sự kiện bàn phím Enter / theo dõi vị trí cuộn
    sync_composer_state()
    ui.timer(
        0.15,
        lambda: ui.run_javascript(
            """
            (function() {
                const msgBox = document.getElementById('chat-messages');
                if (msgBox && !msgBox.__scrollBound) {
                    msgBox.__scrollBound = true;
                    window.__chatNearBottom = true;
                    msgBox.addEventListener('scroll', () => {
                        const dist = msgBox.scrollHeight - msgBox.scrollTop - msgBox.clientHeight;
                        window.__chatNearBottom = dist < 120;
                    });
                }
                const ta = document.querySelector('.composer-textarea textarea');
                if (ta && !ta.__enterBound) {
                    ta.__enterBound = true;
                    ta.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            const btn = document.getElementById('composer-send-btn');
                            if (btn && !btn.disabled) btn.click();
                        }
                    });
                }
            })();
            """
        ),
        once=True,
    )
    ui.timer(0.5, tick)
    ui.timer(0.1, check_api, once=True)
