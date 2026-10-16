"""Client LLM chuẩn OpenAI (Gemini/Groq đổi bằng .env), cache xuống đĩa, đếm lượt gọi."""
import hashlib
import json
import os
import re
from pathlib import Path

CACHE_DIR = Path(".cache/llm")
DEFAULT_MAX_RETRIES = 8  # SDK openai tự chờ lũy tiến và thử lại khi gặp 429/5xx
JSON_RETRY_HINT = "Chỉ trả về một đối tượng JSON hợp lệ, không kèm giải thích."
_JSON_RE = re.compile(r"\{.*\}", re.S)


class LLM:
    """Client LLM chuẩn OpenAI: cache kết quả xuống đĩa, đếm lượt gọi API thật (`calls`)."""
    def __init__(self, client, model, cache_dir=CACHE_DIR):
        self.client = client
        self.model = model
        self.cache_dir = Path(cache_dir)
        self.calls = 0  # lượt gọi API thật, không tính cache

    def _cache_path(self, messages, params):
        raw = json.dumps({"model": self.model, "messages": messages, "params": params},
                         ensure_ascii=False, sort_keys=True)
        return self.cache_dir / f"{hashlib.sha256(raw.encode()).hexdigest()}.json"

    def chat(self, messages, temperature=0.0, **params):
        """Gọi LLM một lượt hội thoại, ưu tiên lấy từ cache đĩa.

        Args:
            messages: danh sách {"role", "content"} theo chuẩn OpenAI.
            temperature: mặc định 0 để kết quả lặp lại được và cache có tác dụng.
            **params: tham số khác chuyển thẳng cho API (đều nằm trong khóa cache).

        Returns:
            Nội dung trả lời; chuỗi rỗng nếu API không trả nội dung (phản hồi rỗng không được cache).
        """
        params = {"temperature": temperature, **params}
        path = self._cache_path(messages, params)
        try:
            return json.loads(path.read_text(encoding="utf-8"))["content"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass  # chưa có hoặc file cache hỏng: gọi API
        resp = self.client.chat.completions.create(model=self.model, messages=messages, **params)
        self.calls += 1
        content = (resp.choices[0].message.content if resp.choices else None) or ""
        if content:  # không cache phản hồi rỗng (bị chặn, lỗi tạm) để lần sau còn gọi lại
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps({"content": content}, ensure_ascii=False), encoding="utf-8")
            tmp.replace(path)  # ghi nguyên tử: dừng giữa chừng không để lại file cache hỏng
        return content

    def chat_json(self, messages, **params):
        """Thử lại 1 lần với lời nhắc chỉ trả JSON; vẫn hỏng thì ValueError để nút gọi tự dùng giá trị mặc định."""
        retry = messages + [{"role": "user", "content": JSON_RETRY_HINT}]
        for attempt in (messages, retry):
            parsed = parse_json(self.chat(attempt, **params))
            if parsed is not None:
                return parsed
        raise ValueError("LLM không trả về JSON hợp lệ sau 2 lần")


def parse_json(text):
    """Đối tượng JSON trong text (bỏ ```json và lời dẫn); None nếu không có."""
    m = _JSON_RE.search(text or "")
    if not m:
        return None
    try:
        value = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _load_env_file(path=".env"):
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


def from_env(prefix="LLM", cache_dir=CACHE_DIR):
    """LLM từ <prefix>_BASE_URL, <prefix>_API_KEY, <prefix>_MODEL; prefix JUDGE cho bộ chấm."""
    from openai import OpenAI
    _load_env_file()
    missing = [f"{prefix}_{k}" for k in ("BASE_URL", "API_KEY", "MODEL") if not os.environ.get(f"{prefix}_{k}")]
    if missing:
        raise RuntimeError(f"thiếu biến môi trường: {', '.join(missing)} (xem .env.example)")
    client = OpenAI(base_url=os.environ[f"{prefix}_BASE_URL"], api_key=os.environ[f"{prefix}_API_KEY"],
                    max_retries=int(os.environ.get(f"{prefix}_MAX_RETRIES", DEFAULT_MAX_RETRIES)))
    return LLM(client, os.environ[f"{prefix}_MODEL"], cache_dir)
