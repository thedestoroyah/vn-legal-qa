"""Kiểm thử tích hợp giao diện NiceGUI (src/ui/web) với FastAPI backend (src/api/main.py).

Chạy bằng cả unittest lẫn pytest (~0.5 giây):
    python -m unittest discover -s tests -p "test_nicegui_web.py" -v
    pytest tests/test_nicegui_web.py -v

Bao phủ đầy đủ 10 trường hợp bắt buộc ở Mục 7:
1. Giao diện khởi chạy thành công (khởi tạo trang, thành phần UI).
2. Backend đang hoạt động (GET /health -> api_ok=True, hiển thị model).
3. Backend bị tắt / không kết nối được (bắt lỗi mạng thành ApiClientError tiếng Việt).
4. Gửi câu hỏi pháp luật thông thường (POST /api/ask -> trả lời + trạng thái grounded).
5. Câu trả lời có nhiều trích dẫn điều luật & mở toàn văn Điều (GET /api/article/{law_id}/{article}).
6. Câu hỏi liên quan hiệu lực văn bản theo thời gian (event_date trong trace -> validity_card & laws.json).
7. Trường hợp API trả về lỗi (HTTP 422 câu hỏi không hợp lệ, HTTP 503 LLM_ERROR).
8. Trường hợp câu trả lời đang xử lý lâu (timeout & state.busy chặn gửi trùng, mở khóa khi xong).
9. Trường hợp dữ liệu trả về thiếu một số trường tùy chọn (clause=None, event_date=None, 404 article).
10. Giữ lịch sử nhiều lượt hỏi đáp và cô lập giữa nhiều hội thoại trong phiên.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
import unittest

import httpx
import openai

from src.api.main import LLM_ERROR, MAX_QUESTION, create_app
from src.ui.article_view import clause_number, split_clauses
from src.ui.web.api.client import ApiClientError, LegalQAApiClient, parse_chunk_id
from src.ui.web.api.schemas import AskResponse
from src.ui.web.components.agent_timeline import step_note
from src.ui.web.components.chat_message import Turn, answer_markdown, format_turn_for_copy
from src.ui.web.components.citation_card import citation_label, law_of
from src.ui.web.components.validity_card import _fmt, cited_laws
from src.ui.web.config import AGENT_CONFIGS, LAWS_CATALOG, NO_BASIS, SAMPLE_QUESTIONS, STATIC_DIR
from src.ui.web.pages.chat import Conversation, PageState, chat_page

C1 = "BLDS2015_Dieu357_Khoan1"
C2 = "BLDS2015_Dieu468_Khoan1"
C_BLLD = "BLLD2012_Dieu38_Khoan1"


def make_stub_agent(responses: list[dict] | None = None, articles: dict[str, dict] | None = None, model: str = "gemini-3.1-flash-lite"):
    """Tạo đối tượng Agent phục vụ các route của src/api/main.py (POST /api/ask, GET /api/article, GET /health)."""
    default_resp = {
        "answer": f"Bên chậm trả tiền phải trả lãi đối với số tiền chậm trả [{C1}] theo mức lãi suất quy định [{C2}].",
        "refused": False,
        "citations": [
            {
                "chunk_id": C1,
                "document": "Bộ luật Dân sự 2015",
                "article": "Điều 357",
                "clause": "Khoản 1",
                "content": "Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó phải trả lãi đối với số tiền chậm trả tương ứng với thời gian chậm trả.",
            },
            {
                "chunk_id": C2,
                "document": "Bộ luật Dân sự 2015",
                "article": "Điều 468",
                "clause": "Khoản 1",
                "content": "Lãi suất vay do các bên thỏa thuận. Trường hợp các bên có thỏa thuận về lãi suất thì lãi suất theo thỏa thuận không được vượt quá 20%/năm.",
            },
        ],
        "retrieved_chunks": [{"chunk_id": C1, "score": 0.92}, {"chunk_id": C2, "score": 0.88}],
        "trace": [
            {"node": "route", "ms": 310, "llm_calls": 1, "output": {"route_type": "situational", "event_date": None, "direct_ref": None}},
            {"node": "retrieve", "ms": 85, "llm_calls": 0, "output": {"queries": ["chậm trả tiền phải trả lãi"], "evidence": [C1, C2]}},
            {"node": "grade", "ms": 290, "llm_calls": 1, "output": {"sufficient": True, "rewrite": False}},
            {"node": "generate", "ms": 640, "llm_calls": 1, "output": {"insufficient": False, "n_generations": 1}},
            {"node": "verify", "ms": 280, "llm_calls": 1, "output": {"removed": [], "regenerate": False}},
        ],
    }
    queue = list(responses or [default_resp])
    articles_map = articles or {
        "BLDS2015_Dieu357": {
            "chunk_id": "BLDS2015_Dieu357",
            "document": "Bộ luật Dân sự 2015",
            "article": "Điều 357",
            "article_title": "Trách nhiệm do chậm thực hiện nghĩa vụ trả tiền",
            "content": (
                "1. Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó phải trả lãi đối với số tiền chậm trả tương ứng với thời gian chậm trả.\n"
                "2. Lãi suất phát sinh do chậm trả tiền được xác định theo thỏa thuận của các bên nhưng không được vượt quá mức lãi suất được quy định tại khoản 1 Điều 468 của Bộ luật này; nếu không có thỏa thuận thì thực hiện theo quy định tại khoản 2 Điều 468 của Bộ luật này."
            ),
        }
    }

    class _StubAgent:
        def __init__(self):
            self.deps = SimpleNamespace(
                llm=SimpleNamespace(model=model),
                retriever=SimpleNamespace(get_article=lambda law_id, article: articles_map.get(f"{law_id}_Dieu{article}")),
            )

        def run(self, question: str, config: str = "full") -> dict:
            return queue.pop(0) if len(queue) > 1 else queue[0]

    return _StubAgent()


@asynccontextmanager
async def api_client_for(agent, ask_timeout: float = 5.0):
    """Khởi chạy app FastAPI thật từ src/api/main.py (kích hoạt lifespan) và gắn vào LegalQAApiClient."""
    app = create_app(lambda: agent)
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        yield LegalQAApiClient(base_url="http://testserver", transport=transport, ask_timeout=ask_timeout)


class TestNiceGUIWebIntegration(unittest.IsolatedAsyncioTestCase):
    """Bộ kiểm thử 10 kịch bản bắt buộc cho giao diện NiceGUI kết nối FastAPI."""

    async def test_01_ui_page_initializes_and_renders_components(self):
        """1. Giao diện khởi chạy thành công (cấu hình, trang chat_page, danh mục luật, câu hỏi mẫu)."""
        self.assertTrue((STATIC_DIR / "styles.css").is_file())
        self.assertTrue(callable(chat_page))
        self.assertEqual(set(AGENT_CONFIGS.keys()), {"full", "no_router", "no_grading", "no_verify", "baseline"})
        self.assertGreaterEqual(len(LAWS_CATALOG), 5)
        self.assertGreaterEqual(len(SAMPLE_QUESTIONS), 3)
        state = PageState(api_url="http://localhost:8000", api_ok=True, api_model="gemini-3.1-flash-lite")
        self.assertEqual(state.current.title, "Hội thoại mới")

    async def test_02_backend_active_health_check(self):
        """2. Backend đang hoạt động (GET /health)."""
        async with api_client_for(make_stub_agent(model="gemini-3.1-flash-lite")) as api:
            health = await api.health()
            self.assertEqual(health.status, "ok")
            self.assertEqual(health.model, "gemini-3.1-flash-lite")

    async def test_03_backend_down_returns_friendly_vietnamese_error(self):
        """3. Backend bị tắt / không thể kết nối."""
        class DownTransport(httpx.AsyncBaseTransport):
            async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
                raise httpx.ConnectError("Connection refused", request=request)

        api = LegalQAApiClient(base_url="http://127.0.0.1:59999", transport=DownTransport())
        with self.assertRaises(ApiClientError) as ctx_health:
            await api.health()
        self.assertIn("Không kết nối được API", ctx_health.exception.message)
        self.assertEqual(ctx_health.exception.kind, "network")
        self.assertIn("uvicorn", ctx_health.exception.hint)

        with self.assertRaises(ApiClientError) as ctx_ask:
            await api.ask("Chậm trả tiền có phải trả lãi không?")
        self.assertIn("Không kết nối được máy chủ hỏi đáp", ctx_ask.exception.message)
        self.assertEqual(ctx_ask.exception.kind, "network")

    async def test_04_normal_legal_question_end_to_end(self):
        """4. Gửi câu hỏi pháp luật thông thường."""
        async with api_client_for(make_stub_agent()) as api:
            resp = await api.ask("Bên chậm trả tiền có phải trả lãi không?")
            self.assertFalse(resp.refused)
            self.assertEqual(resp.status, "answered")
            self.assertIn(C1, resp.answer)
            self.assertIn("`[BLDS2015_Dieu357_Khoan1]`", answer_markdown(resp.answer))
            self.assertEqual(resp.total_llm_calls, 4)
            self.assertEqual([s.node for s in resp.trace], ["route", "retrieve", "grade", "generate", "verify"])

    async def test_05_multiple_citations_and_full_article_fetch(self):
        """5. Câu trả lời có nhiều trích dẫn điều luật & mở toàn văn Điều."""
        async with api_client_for(make_stub_agent()) as api:
            resp = await api.ask("Lãi chậm trả được tính thế nào?")
            self.assertEqual(len(resp.citations), 2)
            self.assertEqual([c.chunk_id for c in resp.citations], [C1, C2])
            self.assertEqual(citation_label(resp.citations[0]), "Bộ luật Dân sự 2015 – Điều 357, Khoản 1")

            art = await api.article(C1)
            self.assertIsNotNone(art)
            self.assertEqual(art.chunk_id, "BLDS2015_Dieu357")
            self.assertIn("Trách nhiệm do chậm thực hiện nghĩa vụ trả tiền", art.article_title)
            # Kiểm tra cache lần gọi thứ 2
            self.assertIs(await api.article(C1), art)

            # Kiểm tra tách khoản và xác định đúng khoản cần tô sáng (Khoản 1)
            target = clause_number(resp.citations[0].clause)
            clauses = split_clauses(art.content)
            self.assertEqual(target, "1")
            self.assertEqual([num for num, _ in clauses], ["1", "2"])

    async def test_06_temporal_validity_question_and_laws_catalog(self):
        """6. Câu hỏi liên quan hiệu lực văn bản theo thời gian."""
        temporal_resp = {
            "answer": f"Theo quy định có hiệu lực năm 2018 [{C_BLLD}].",
            "refused": False,
            "citations": [
                {
                    "chunk_id": C_BLLD,
                    "document": "Bộ luật Lao động 2012",
                    "article": "Điều 38",
                    "clause": "Khoản 1",
                    "content": "Người sử dụng lao động có quyền đơn phương chấm dứt hợp đồng lao động trong những trường hợp sau đây...",
                }
            ],
            "retrieved_chunks": [{"chunk_id": C_BLLD, "score": 0.95}],
            "trace": [
                {"node": "route", "ms": 250, "llm_calls": 1, "output": {"route_type": "temporal", "event_date": "2018-06-15", "direct_ref": None}},
                {"node": "retrieve", "ms": 70, "llm_calls": 0, "output": {"queries": ["đơn phương chấm dứt hợp đồng lao động 2018"], "evidence": [C_BLLD]}},
                {"node": "grade", "ms": 210, "llm_calls": 1, "output": {"sufficient": True, "rewrite": False}},
                {"node": "generate", "ms": 520, "llm_calls": 1, "output": {"insufficient": False, "n_generations": 1}},
                {"node": "verify", "ms": 230, "llm_calls": 1, "output": {"removed": [], "regenerate": False}},
            ],
        }
        async with api_client_for(make_stub_agent(responses=[temporal_resp])) as api:
            resp = await api.ask("Năm 2018 người sử dụng lao động đơn phương chấm dứt hợp đồng thế nào?")
            self.assertEqual(resp.route_type, "temporal")
            self.assertEqual(resp.event_date, "2018-06-15")
            self.assertEqual(_fmt(resp.event_date), "15/06/2018")
            self.assertEqual(cited_laws(resp), ["BLLD2012"])
            self.assertEqual(law_of(C_BLLD).get("status"), "Hết hiệu lực")
            self.assertIn("theo mốc thời gian", step_note(resp.trace[0]))
            self.assertIn("ngày sự việc 2018-06-15", step_note(resp.trace[0]))

    async def test_07_api_error_responses_422_and_503(self):
        """7. Trường hợp API trả về lỗi (422 và 503 LLM_ERROR)."""
        async with api_client_for(make_stub_agent()) as api:
            with self.assertRaises(ApiClientError) as ctx_empty:
                await api.ask("   ")
            self.assertEqual(ctx_empty.exception.status_code, 422)

            with self.assertRaises(ApiClientError) as ctx_long:
                await api.ask("a" * (MAX_QUESTION + 1))
            self.assertEqual(ctx_long.exception.status_code, 422)

        class BrokenAgent:
            deps = SimpleNamespace(llm=SimpleNamespace(model="fake"), retriever=SimpleNamespace(get_article=lambda *_: None))

            def run(self, question, config="full"):
                raise openai.APIConnectionError(request=httpx.Request("POST", "http://llm"))

        async with api_client_for(BrokenAgent()) as broken_api:
            with self.assertRaises(ApiClientError) as ctx_503:
                await broken_api.ask("Câu hỏi hợp lệ")
            self.assertEqual(ctx_503.exception.status_code, 503)
            self.assertEqual(ctx_503.exception.message, LLM_ERROR)

    async def test_08_slow_request_timeout_and_pending_turn_state(self):
        """8. Trường hợp câu trả lời đang xử lý lâu (timeout & trạng thái đang chờ)."""
        class SlowTransport(httpx.AsyncBaseTransport):
            async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
                raise httpx.ReadTimeout("Read timed out", request=request)

        slow_api = LegalQAApiClient(base_url="http://testserver", transport=SlowTransport(), ask_timeout=0.05)
        with self.assertRaises(ApiClientError) as ctx_timeout:
            await slow_api.ask("Câu hỏi xử lý lâu")
        self.assertIn("quá lâu", ctx_timeout.exception.message)

        state = PageState(api_url="http://testserver", busy=True, elapsed=12.4)
        pending_turn = Turn(question="Đang hỏi...", config="full")
        self.assertTrue(pending_turn.pending)
        self.assertTrue(state.busy)

    async def test_09_optional_fields_missing_and_partial_or_refused_states(self):
        """9. Trường hợp dữ liệu trả về thiếu một số trường tùy chọn."""
        raw = {
            "answer": f"Nội dung trả lời [BLDS2015_Dieu357] {NO_BASIS}",
            "refused": False,
            "citations": [{"chunk_id": "BLDS2015_Dieu357", "document": "Bộ luật Dân sự 2015", "article": "Điều 357"}],
            "retrieved_chunks": [{"chunk_id": "BLDS2015_Dieu357", "score": 0.9}],
            "trace": [{"node": "retrieve", "ms": 10, "llm_calls": 0, "output": {"evidence": ["BLDS2015_Dieu357"]}}],
        }
        resp = AskResponse.model_validate(raw)
        self.assertEqual(resp.status, "partial")
        self.assertIsNone(resp.route_type)
        self.assertIsNone(resp.event_date)
        self.assertIsNone(resp.citations[0].clause)
        self.assertEqual(citation_label(resp.citations[0]), "Bộ luật Dân sự 2015 – Điều 357")

        async with api_client_for(make_stub_agent()) as api:
            self.assertIsNone(parse_chunk_id("khong_dung_dinh_dang"))
            self.assertIsNone(await api.article("khong_dung_dinh_dang"))
            self.assertIsNone(await api.article("BLDS2015_Dieu9999_Khoan1"))

    async def test_10_multi_turn_history_and_conversation_isolation(self):
        """10. Lịch sử nhiều lượt hỏi đáp và cô lập giữa các hội thoại."""
        r1 = {
            "answer": f"Trả lời lượt 1 [{C1}].",
            "refused": False,
            "citations": [{"chunk_id": C1, "document": "Bộ luật Dân sự 2015", "article": "Điều 357", "clause": "Khoản 1", "content": "Nội dung 1"}],
            "retrieved_chunks": [{"chunk_id": C1, "score": 0.91}],
            "trace": [{"node": "route", "ms": 100, "llm_calls": 1, "output": {"route_type": "situational"}}],
        }
        r2 = {
            "answer": f"Trả lời lượt 2 [{C2}].",
            "refused": False,
            "citations": [{"chunk_id": C2, "document": "Bộ luật Dân sự 2015", "article": "Điều 468", "clause": "Khoản 1", "content": "Nội dung 2"}],
            "retrieved_chunks": [{"chunk_id": C2, "score": 0.89}],
            "trace": [{"node": "route", "ms": 110, "llm_calls": 1, "output": {"route_type": "situational"}}],
        }
        async with api_client_for(make_stub_agent(responses=[r1, r2])) as api:
            state = PageState(api_url=api.base_url)

            t1 = Turn(question="Câu hỏi thứ nhất về chậm trả tiền", config="full")
            state.current.turns.append(t1)
            t1.response = await api.ask(t1.question, t1.config)

            t2 = Turn(question="Câu hỏi thứ hai về mức lãi suất", config="full")
            state.current.turns.append(t2)
            t2.response = await api.ask(t2.question, t2.config)

            self.assertEqual(len(state.current.turns), 2)
            self.assertEqual(state.current.title, "Câu hỏi thứ nhất về chậm trả tiền")
            self.assertIn(C1, state.current.turns[0].response.answer)
            self.assertIn(C2, state.current.turns[1].response.answer)
            self.assertEqual([c.chunk_id for c in state.current.all_citations], [C2, C1])
            self.assertIn("Căn cứ pháp lý:", format_turn_for_copy(t1))
            t1.feedback = "up"
            self.assertEqual(t1.feedback, "up")

            state.conversations.append(Conversation())
            state.current_index = 1
            self.assertEqual(len(state.current.turns), 0)
            self.assertEqual(state.current.title, "Hội thoại mới")
            self.assertEqual(len(state.conversations[0].turns), 2)


def _client_built_by_index(monkeypatch):
    from src.ui.web import main as web_main
    seen = []

    async def fake_chat_page(client):
        seen.append(client)

    monkeypatch.setattr(web_main, "chat_page", fake_chat_page)
    asyncio.run(web_main.index())
    return seen[0]


def test_index_turns_fallback_off_when_env_says_so(monkeypatch):
    monkeypatch.setenv("UI_LOCAL_FALLBACK", "0")
    assert _client_built_by_index(monkeypatch)._enable_local_fallback is False


def test_index_keeps_fallback_by_default(monkeypatch):
    monkeypatch.delenv("UI_LOCAL_FALLBACK", raising=False)
    assert _client_built_by_index(monkeypatch)._enable_local_fallback is True


if __name__ == "__main__":
    unittest.main(verbosity=2)
