"""Client LLM chuẩn OpenAI (Gemini/Groq đổi bằng .env), cache xuống đĩa, đếm lượt gọi, giãn cách theo RPM."""
import hashlib
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"  # gốc repo: chạy lệnh từ thư mục nào (vd src/ui) cũng nạp đúng .env
CACHE_DIR = ROOT / ".cache" / "llm"
DEFAULT_MAX_RETRIES = 8  # SDK openai tự chờ lũy tiến và thử lại khi gặp 429/5xx
JSON_RETRY_HINT = "Chỉ trả về một đối tượng JSON hợp lệ, không kèm giải thích."
_DECODER = json.JSONDecoder()


class LLM:
    """Client LLM chuẩn OpenAI: cache kết quả xuống đĩa, đếm lượt gọi, giãn cách giữa các lượt gọi thật.

    Thuộc tính `calls` đếm lượt gọi API thật; `requests` đếm lượt gọi logic (kể cả trúng cache).
    """

    def __init__(self, client, model, cache_dir=CACHE_DIR, base_url="", min_interval=0.0):
        self.client = client
        self.model = model
        self.cache_dir = Path(cache_dir)
        self.base_url = base_url
        self.min_interval = min_interval  # giây tối thiểu giữa 2 lượt gọi thật; Gemini free tier 15 RPM → 4.2
        self.calls = 0
        self.waited = 0.0  # tổng giây đã ngủ để giãn cách; trace trừ phần này ra khỏi thời gian của nút
        self.requests = 0  # "lượt gọi LLM/câu" của RQ3 không phụ thuộc cache nên đếm cả lượt trúng cache
        self._last_call = None

    def _cache_path(self, messages, params):
        raw = json.dumps({"base_url": self.base_url, "model": self.model, "messages": messages, "params": params},
                         ensure_ascii=False, sort_keys=True)
        return self.cache_dir / f"{hashlib.sha256(raw.encode()).hexdigest()}.json"

    def _throttle(self):
        if self._last_call is not None:
            wait = self.min_interval - (time.monotonic() - self._last_call)
            if wait > 0:
                time.sleep(wait)
                self.waited += wait
        self._last_call = time.monotonic()

    def chat(self, messages, temperature=0.0, **params):
        """Gọi LLM một lượt hội thoại, ưu tiên lấy từ cache đĩa.

        Args:
            messages: danh sách {"role", "content"} theo chuẩn OpenAI.
            temperature: mặc định 0 để kết quả lặp lại được và cache có tác dụng.
            **params: tham số khác chuyển thẳng cho API (đều nằm trong khóa cache).

        Returns:
            Nội dung trả lời; chuỗi rỗng nếu API không trả nội dung (phản hồi rỗng không được cache).
        """
        self.requests += 1
        params = {"temperature": temperature, **params}
        path = self._cache_path(messages, params)
        try:
            return json.loads(path.read_text(encoding="utf-8"))["content"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass  # chưa có hoặc file cache hỏng: gọi API
        self._throttle()
        resp = self.client.chat.completions.create(model=self.model, messages=messages, **params)
        self.calls += 1
        content = (resp.choices[0].message.content if resp.choices else None) or ""
        if content:  # không cache phản hồi rỗng (bị chặn, lỗi tạm) để lần sau còn gọi lại
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(f".{os.getpid()}.tmp")  # mỗi tiến trình một file tạm: chạy song song không ghi đè nhau
            tmp.write_text(json.dumps({"content": content}, ensure_ascii=False), encoding="utf-8")
            tmp.replace(path)  # ghi nguyên tử: dừng giữa chừng không để lại file cache hỏng
        return content

    def chat_json(self, messages, temperature=0.0, **params):
        """Gọi LLM và đọc kết quả thành dict JSON; thử lại 1 lần kèm lời nhắc chỉ trả JSON.

        Args:
            messages, temperature, **params: như `chat`.

        Returns:
            dict đọc từ phản hồi.

        Raises:
            ValueError: sau 2 lần vẫn không có JSON hợp lệ; nút gọi tự dùng giá trị mặc định.
        """
        retry = messages + [{"role": "user", "content": JSON_RETRY_HINT}]
        for attempt in (messages, retry):
            parsed = parse_json(self.chat(attempt, temperature, **params))
            if parsed is not None:
                return parsed
            # bỏ bản cache hỏng: lần chạy sau gọi lại API thay vì lặp lại đúng câu trả lời hỏng
            self._cache_path(attempt, {"temperature": temperature, **params}).unlink(missing_ok=True)
        raise ValueError("LLM không trả về JSON hợp lệ sau 2 lần")


def parse_json(text):
    """Lấy đối tượng JSON hợp lệ đầu tiên trong `text` (bỏ ```json, lời dẫn, ngoặc nhọn lạc).

    Returns:
        dict; None nếu không có đối tượng JSON nào.
    """
    text = text or ""
    for start, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            value, _ = _DECODER.raw_decode(text, start)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None


def _load_env_file(path=ENV_PATH):
    """Nạp KEY=VALUE từ .env, không ghi đè biến đã có trong shell."""
    # shortcut: không hỗ trợ export, giá trị nhiều dòng, comment cuối dòng; đổi sang python-dotenv nếu .env phức tạp hơn
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def from_env(prefix="LLM", cache_dir=CACHE_DIR, env_path=ENV_PATH, max_retries=None, timeout=None):
    """Dựng LLM từ biến môi trường hoặc file .env.

    Args:
        prefix: "LLM" cho tác tử, "JUDGE" cho bộ chấm. Đọc <prefix>_BASE_URL, _API_KEY, _MODEL
            (bắt buộc) và _MIN_INTERVAL, _MAX_RETRIES (tùy chọn).
        cache_dir: thư mục cache.
        env_path: đường dẫn file .env (mặc định ở gốc repo).
        max_retries: số lần SDK thử lại khi gặp 429/5xx; None thì đọc <prefix>_MAX_RETRIES (mặc định 8).
        timeout: giây chờ tối đa mỗi lượt gọi; None dùng mặc định của SDK (600 s).

    Raises:
        RuntimeError: thiếu biến bắt buộc.
    """
    from openai import OpenAI
    _load_env_file(env_path)
    missing = [f"{prefix}_{k}" for k in ("BASE_URL", "API_KEY", "MODEL") if not os.environ.get(f"{prefix}_{k}")]
    if missing:
        raise RuntimeError(f"thiếu biến môi trường: {', '.join(missing)} (xem .env.example)")
    base_url = os.environ[f"{prefix}_BASE_URL"]
    extra = {} if timeout is None else {"timeout": timeout}
    client = OpenAI(base_url=base_url, api_key=os.environ[f"{prefix}_API_KEY"], **extra,
                    max_retries=max_retries if max_retries is not None
                    else int(os.environ.get(f"{prefix}_MAX_RETRIES", DEFAULT_MAX_RETRIES)))
    return LLM(client, os.environ[f"{prefix}_MODEL"], cache_dir, base_url,
               float(os.environ.get(f"{prefix}_MIN_INTERVAL", 0)))
