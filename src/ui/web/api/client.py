"""Client HTTP bất đồng bộ (httpx) gọi src/api/main.py; mọi lỗi được đổi thành ApiClientError có câu tiếng Việt."""
from __future__ import annotations

import re

import httpx
from pydantic import ValidationError

from src.ui.article_view import article_key
from src.ui.web.api.schemas import ArticleResponse, AskResponse, HealthResponse
from src.ui.web.config import API_URL, ARTICLE_TIMEOUT, ASK_TIMEOUT, HEALTH_TIMEOUT, MAX_QUESTION


class ApiClientError(Exception):
    """Lỗi gọi API, mang câu thông báo tiếng Việt thân thiện và phân loại lỗi để UI hiển thị."""

    def __init__(self, message: str, status_code: int | None = None, kind: str = "server", hint: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.kind = kind
        self.hint = hint


def parse_chunk_id(chunk_id: str) -> tuple[str, str] | None:
    """BLDS2015_Dieu357_Khoan1 -> ('BLDS2015', '357'); None nếu không đúng dạng."""
    m = re.fullmatch(r"([A-Za-z]+\d{4})_Dieu(\w+)", article_key(chunk_id or ""))
    return (m[1], m[2]) if m else None


def _detail(resp: httpx.Response) -> str | None:
    try:
        detail = resp.json().get("detail")
    except (ValueError, AttributeError):
        return None
    return detail.strip() if isinstance(detail, str) and detail.strip() else None


class LegalQAApiClient:
    """Gọi 3 endpoint của backend: GET /health, POST /api/ask, GET /api/article/{law_id}/{article}."""

    def __init__(self, base_url: str | None = None, transport: httpx.AsyncBaseTransport | None = None,
                 ask_timeout: float = ASK_TIMEOUT, enable_local_fallback: bool = False) -> None:
        self.base_url = (API_URL if base_url is None else base_url).rstrip("/")
        self.ask_timeout = ask_timeout
        self._transport = transport  # test truyền ASGITransport để gọi app FastAPI thật trong tiến trình
        self._enable_local_fallback = enable_local_fallback and (transport is None)
        self._using_fallback = False
        self._articles: dict[str, ArticleResponse] = {}

    def _http(self, timeout: float, use_fallback: bool = False) -> httpx.AsyncClient:
        if use_fallback:
            from src.ui.web.api.local_fallback import get_fallback_transport
            return httpx.AsyncClient(base_url="http://local-backend", timeout=timeout, transport=get_fallback_transport())
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout, connect=min(timeout, 1.5)),
            transport=self._transport,
        )

    async def _request(self, method: str, path: str, timeout: float, **kwargs) -> httpx.Response:
        try:
            async with self._http(timeout, use_fallback=False) as http:
                resp = await http.request(method, path, **kwargs)
                self._using_fallback = False
                return resp
        except httpx.ConnectError:
            if not self._enable_local_fallback:
                raise
            self._using_fallback = True
            async with self._http(timeout, use_fallback=True) as http:
                return await http.request(method, path, **kwargs)

    async def health(self) -> HealthResponse:
        try:
            resp = await self._request("GET", "/health", HEALTH_TIMEOUT)
        except httpx.TimeoutException as exc:
            raise ApiClientError(
                f"Máy chủ API tại {self.base_url} phản hồi quá chậm.",
                kind="timeout",
                hint="Máy chủ có thể đang nạp mô hình embedding (~30s). Hãy bấm Kiểm tra lại sau giây lát.",
            ) from exc
        except httpx.HTTPError as exc:
            raise ApiClientError(
                f"Không kết nối được API tại {self.base_url}.",
                kind="network",
                hint="Hãy khởi động backend: uvicorn src.api.main:app --port 8000",
            ) from exc
        if resp.status_code != 200:
            raise ApiClientError(f"API trả mã {resp.status_code} ở /health.", resp.status_code, kind="server")
        try:
            return HealthResponse.model_validate(resp.json())
        except (ValueError, ValidationError) as exc:
            raise ApiClientError("Phản hồi /health không đúng định dạng.", kind="schema") from exc

    async def ask(self, question: str, config: str = "full") -> AskResponse:
        """Gửi câu hỏi; kiểm tra rỗng/độ dài trước để báo lỗi nhanh (backend vẫn kiểm lại và trả 422)."""
        question = (question or "").strip()
        if not question:
            raise ApiClientError("Vui lòng nhập câu hỏi.", 422, kind="validation")
        if len(question) > MAX_QUESTION:
            raise ApiClientError(
                f"Câu hỏi dài {len(question)} ký tự, vượt quá giới hạn tối đa {MAX_QUESTION} ký tự.",
                422,
                kind="validation",
            )
        try:
            resp = await self._request("POST", "/api/ask", self.ask_timeout, json={"question": question, "config": config})
        except httpx.TimeoutException as exc:
            raise ApiClientError(
                "Máy chủ trả lời quá lâu. Vui lòng thử lại sau.",
                kind="timeout",
                hint="Tác tử LLM có thể đang giãn cách tốc độ gọi (RPM). Bạn có thể bấm 'Thử lại' ngay bên dưới.",
            ) from exc
        except httpx.HTTPError as exc:
            raise ApiClientError(
                "Không kết nối được máy chủ hỏi đáp. Kiểm tra API đã chạy chưa.",
                kind="network",
                hint=f"Đảm bảo FastAPI đang chạy tại {self.base_url} (uvicorn src.api.main:app --port 8000).",
            ) from exc
        if resp.status_code == 422:
            raise ApiClientError("Câu hỏi không hợp lệ (rỗng hoặc dài quá 1000 ký tự).", 422, kind="validation")
        if resp.status_code != 200:
            # 503: backend gửi sẵn câu thông báo tiếng Việt (LLM_ERROR) -> hiển thị nguyên văn
            raise ApiClientError(
                _detail(resp) or f"Lỗi máy chủ ({resp.status_code}).",
                resp.status_code,
                kind="server",
                hint="Bạn có thể đợi vài giây rồi bấm nút 'Thử lại' trên câu hỏi này.",
            )
        try:
            return AskResponse.model_validate(resp.json())
        except (ValueError, ValidationError) as exc:
            raise ApiClientError(
                "Phản hồi của máy chủ không đúng định dạng Phụ lục A.5.",
                kind="schema",
            ) from exc

    async def article(self, chunk_id: str) -> ArticleResponse | None:
        """Toàn văn Điều chứa chunk_id; None nếu sai dạng, 404, lỗi mạng hoặc sai định dạng."""
        parsed = parse_chunk_id(chunk_id)
        if parsed is None:
            return None
        key = "_Dieu".join(parsed)
        if key in self._articles:
            return self._articles[key]
        try:
            resp = await self._request("GET", f"/api/article/{parsed[0]}/{parsed[1]}", ARTICLE_TIMEOUT)
        except httpx.HTTPError:
            return None
        if resp.status_code != 200:
            return None
        try:
            art = ArticleResponse.model_validate(resp.json())
        except (ValueError, ValidationError):
            return None
        self._articles[key] = art
        return art
