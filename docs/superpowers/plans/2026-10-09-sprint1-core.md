# Sprint 1 (phần Đạt): Hiệu lực, fixed-chunk theo Điều, LLM client — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hoàn thành các việc S1 còn lại của Đạt: chunk mang `expiry_date` và index lọc được theo khoảng hiệu lực; `fixed_chunk` ghi các Điều mà mỗi đoạn phủ qua; `src/generation/llm.py` (client chuẩn OpenAI, cache đĩa, retry 429, đếm lượt gọi, `chat_json`).

**Architecture:** Sửa nhỏ `legal_chunker.py` và `index.py` hiện có; thêm một module `llm.py` độc lập, nhận client được tiêm vào (để test bằng client giả), retry 429 giao cho SDK `openai` (`max_retries`), cache là file JSON theo hash của request.

**Tech Stack:** Python 3.14 (.venv), pytest 9.1.1, chromadb 1.5.9, openai 3.26.1.

**Spec:** `docs/superpowers/specs/2026-10-09-agentic-legal-qa-design.md` (mục 3, 4, 6, 9). Định dạng dữ liệu: Phụ lục A trong `Đề cương DACNTT.txt`.

## Global Constraints

- Chạy mọi lệnh từ thư mục gốc repo `vn-legal-qa/`; chạy test bằng `.venv/bin/python -m pytest -q`.
- Không thêm thư viện mới; chỉ dùng thư viện đã pin trong `requirements.txt`.
- Ngày dạng ISO `"YYYY-MM-DD"`; `expiry_date = null` nghĩa là còn hiệu lực; văn bản có hiệu lực tại ngày `d` khi `effective_date ≤ d < expiry_date`.
- Mọi lượt gọi LLM đi qua `src/generation/llm.py`; đổi nhà cung cấp chỉ bằng `.env`, không sửa code.
- Comment bằng tiếng Việt, chỉ giải thích "tại sao", giống code hiện có.
- **Không commit.** Đạt tự commit; mỗi task kết thúc bằng chạy toàn bộ test.

## Review Focus

- `laws.json` thiếu khóa `expiry_date` (file cũ hoặc Hùng chưa điền) → chunk có `expiry_date = None`, index coi là còn hiệu lực, không crash. Test: Task 1 Step 1.
- Câu dẫn chiếu giữa dòng như "theo quy định tại Điều 5." → không được tính là sang Điều mới trong `fixed_chunk`. Test: Task 2 Step 1.
- Đoạn cố định bắt đầu giữa một Điều (không chứa dòng tiêu đề) → vẫn ghi Điều đang chứa nó. Test: Task 2 Step 1.
- LLM trả nội dung rỗng/`None` (bị chặn an toàn, lỗi tạm) → không được ghi vào cache, lần sau phải gọi lại API. Test: Task 3 Step 1.
- LLM bọc JSON trong ```` ```json ```` hoặc kèm lời dẫn → `chat_json` vẫn đọc được; trả rác hai lần → `ValueError` (nút agent tự dùng giá trị mặc định). Test: Task 3 Step 1.

---

### Task 1: `expiry_date` trong chunk và khoảng hiệu lực dạng số trong index

Chroma chỉ so sánh `$lt/$gte` trên số, nên index lưu thêm `effective_from`/`effective_to` dạng `YYYYMMDD` (số nguyên), văn bản còn hiệu lực có `effective_to = 99991231`. Sprint 2 sẽ lọc bằng hai trường này.

**Files:**
- Modify: `src/ingestion/legal_chunker.py:22-34` (hàm `_base`)
- Modify: `src/ingestion/index.py:1-48` (thêm `chunk_metadata`, dùng trong `build_index`)
- Modify: `data/raw/laws.json` (thêm `"expiry_date": null` cho 4 luật)
- Test: `tests/test_legal_chunker.py`, `tests/test_index.py`

**Interfaces:**
- Consumes: `chunk_law(text, meta)`, `build_index(chunks, embed, db_path, rebuild)` hiện có.
- Produces: mỗi chunk có khóa `"expiry_date"` (str ISO hoặc `None`). `chunk_metadata(chunk) -> dict` trong `src/ingestion/index.py`, trả metadata có `effective_from: int`, `effective_to: int`. Hằng `OPEN_END = 99991231`. Sprint 2 lọc bằng `{"$and": [{"effective_from": {"$lte": d}}, {"effective_to": {"$gt": d}}]}` với `d` dạng `YYYYMMDD`.

- [ ] **Step 1: Viết test thất bại**

Thêm vào cuối `tests/test_legal_chunker.py`:

```python
def test_expiry_date_copied_from_meta():
    meta = {**META, "law_id": "BLLD2012", "expiry_date": "2021-01-01", "status": "Hết hiệu lực"}
    assert {c["expiry_date"] for c in chunk_law(SAMPLE, meta)} == {"2021-01-01"}


def test_missing_expiry_date_means_still_effective(chunks):
    # META không có khóa expiry_date (laws.json cũ) -> coi là còn hiệu lực
    assert all(c["expiry_date"] is None for c in chunks)
```

Trong `tests/test_index.py`, sửa dòng import thành:

```python
from src.ingestion.index import build_index, chunk_metadata, embedding_text
```

và thêm vào cuối file:

```python
def test_chunk_metadata_adds_numeric_validity_range():
    m = chunk_metadata({**CHUNKS[0], "expiry_date": "2021-01-01"})
    assert m["effective_from"] == 20200101
    assert m["effective_to"] == 20210101
    # CHUNKS không có khóa expiry_date -> còn hiệu lực
    assert chunk_metadata(CHUNKS[0])["effective_to"] == 99991231


def test_validity_range_filter_works_in_chroma(tmp_path):
    old = {**CHUNKS[0], "chunk_id": "OLD", "expiry_date": "2021-01-01"}
    col = build_index([old, CHUNKS[1]], fake_embed, tmp_path)

    def valid_at(d):
        where = {"$and": [{"effective_from": {"$lte": d}}, {"effective_to": {"$gt": d}}]}
        return sorted(col.get(where=where)["ids"])

    assert valid_at(20200301) == ["A_Dieu2", "OLD"]
    assert valid_at(20230101) == ["A_Dieu2"]
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `.venv/bin/python -m pytest -q tests/test_legal_chunker.py tests/test_index.py`
Expected: lỗi import `chunk_metadata` (collection error) và `KeyError: 'expiry_date'`.

- [ ] **Step 3: Cài đặt**

Trong `src/ingestion/legal_chunker.py`, hàm `_base`, thêm một dòng ngay sau `"effective_date": meta["effective_date"],`:

```python
        "expiry_date": meta.get("expiry_date"),  # None = còn hiệu lực
```

Trong `src/ingestion/index.py`, thêm sau dòng `DEFAULT_MODEL = "BAAI/bge-m3"`:

```python
OPEN_END = 99991231  # effective_to của văn bản còn hiệu lực


def _date_int(iso):
    return int(iso.replace("-", "")) if iso else OPEN_END


def chunk_metadata(chunk):
    """Metadata cho Chroma: bỏ content và None; thêm khoảng hiệu lực dạng số vì Chroma chỉ so sánh $lt/$gte trên số."""
    meta = {k: v for k, v in chunk.items() if k != "content" and v is not None}
    meta["effective_from"] = _date_int(chunk["effective_date"])
    meta["effective_to"] = _date_int(chunk.get("expiry_date"))
    return meta
```

Trong `build_index`, thay hai dòng:

```python
            # Chroma không nhận giá trị None trong metadata
            metadatas=[{k: v for k, v in c.items() if k != "content" and v is not None} for c in batch],
```

bằng:

```python
            metadatas=[chunk_metadata(c) for c in batch],
```

Trong `data/raw/laws.json`, thêm `"expiry_date": null,` ngay sau dòng `"effective_date"` của cả 4 mục (BLDS2015, BLLD2019, LDN2020, LTM2005). Không thêm BLLD2012 — đó là việc của Hùng (cần đối chiếu nguồn chính thức).

- [ ] **Step 4: Chạy toàn bộ test**

Run: `.venv/bin/python -m pytest -q`
Expected: tất cả PASS (15 test).

---

### Task 2: `fixed_chunk` ghi các Điều mà mỗi đoạn phủ qua

RQ2 so sánh các cách phân đoạn ở cấp Điều; đoạn cố định không có `chunk_id` dạng Khoản nên phải tự ghi danh sách Điều (`articles`). Chỉ dòng tiêu đề (`ARTICLE_RE` neo đầu dòng) mới đổi Điều, để câu dẫn chiếu giữa dòng không bị bắt nhầm.

**Files:**
- Modify: `src/ingestion/legal_chunker.py:91-101` (hàm `fixed_chunk`, thêm `_tagged_words`)
- Test: `tests/test_legal_chunker.py`

**Interfaces:**
- Consumes: `ARTICLE_RE`, `CHAPTER_RE`, `SECTION_RE`, `_clean`, `_base` trong cùng file.
- Produces: mỗi phần tử của `fixed_chunk(text, meta, size=200, overlap=40)` có thêm khóa `"articles": list[str]` (vd `["Điều 1", "Điều 2"]`, theo thứ tự xuất hiện, không trùng; `[]` nếu không thuộc Điều nào). `ValueError` nếu không thỏa `0 <= overlap < size`. Evaluate (Sprint 2) so khớp gold cấp Điều với `chunk["articles"]`.

- [ ] **Step 1: Viết test thất bại**

Thêm vào cuối `tests/test_legal_chunker.py`:

```python
def test_fixed_chunk_records_articles_spanned():
    # mỗi Điều 11 từ: 3 từ tiêu đề + 8 từ nội dung
    text = "Điều 1. A\n" + " ".join(["x"] * 8) + "\nĐiều 2. B\n" + " ".join(["y"] * 8)
    out = fixed_chunk(text, META, size=10, overlap=0)
    assert [c["articles"] for c in out] == [["Điều 1"], ["Điều 1", "Điều 2"], ["Điều 2"]]


def test_fixed_chunk_window_starting_mid_article_keeps_that_article():
    text = "Điều 7. A\n" + " ".join(["x"] * 30)
    out = fixed_chunk(text, META, size=10, overlap=0)
    assert out[2]["articles"] == ["Điều 7"]


def test_fixed_chunk_ignores_inline_article_reference():
    text = "Điều 1. A\nTheo quy định tại Điều 5. thì bên vi phạm phải bồi thường."
    assert fixed_chunk(text, META, size=50, overlap=0)[0]["articles"] == ["Điều 1"]


def test_fixed_chunk_text_outside_articles_has_no_article():
    text = "BỘ LUẬT DÂN SỰ\nChương I\nQUY ĐỊNH CHUNG"
    assert fixed_chunk(text, META, size=50, overlap=0)[0]["articles"] == []


@pytest.mark.parametrize("size, overlap", [(10, 10), (10, 12), (10, -1)])
def test_fixed_chunk_rejects_invalid_overlap(size, overlap):
    with pytest.raises(ValueError):
        fixed_chunk("a b c", META, size=size, overlap=overlap)
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `.venv/bin/python -m pytest -q tests/test_legal_chunker.py`
Expected: FAIL với `KeyError: 'articles'`; các test `rejects_invalid_overlap` FAIL vì không có `ValueError` (hoặc treo/`ValueError: range() arg 3 must not be zero` chỉ ở trường hợp overlap = size).

- [ ] **Step 3: Cài đặt**

Trong `src/ingestion/legal_chunker.py`, thay toàn bộ hàm `fixed_chunk` (dòng 91-101) bằng:

```python
def _tagged_words(text):
    """Các cặp (từ, Điều chứa từ đó). Chỉ dòng tiêu đề mới đổi Điều, tránh bắt nhầm 'theo Điều 5.' giữa câu."""
    current, out = None, []
    for raw in text.splitlines():
        line = _clean(raw)
        if m := ARTICLE_RE.match(line):
            current = f"Điều {m.group(1)}"
        elif CHAPTER_RE.match(line) or SECTION_RE.match(line):
            current = None
        out += [(w, current) for w in line.split()]
    return out


def fixed_chunk(text, meta, size=200, overlap=40):
    """Baseline cắt theo số từ, không theo cấu trúc luật (so sánh RQ2); ghi các Điều mỗi đoạn phủ qua để chấm ở cấp Điều."""
    if not 0 <= overlap < size:
        raise ValueError(f"cần 0 <= overlap < size, nhận overlap={overlap}, size={size}")
    tagged = _tagged_words(text)
    step = size - overlap
    out = []
    for n, start in enumerate(range(0, len(tagged), step)):
        window = tagged[start:start + size]
        out.append({**_base(meta), "chunk_id": f"{meta['law_id']}_fixed{n}",
                    "content": " ".join(w for w, _ in window),
                    "articles": list(dict.fromkeys(a for _, a in window if a))})
        if start + size >= len(tagged):
            break
    return out
```

- [ ] **Step 4: Chạy toàn bộ test**

Run: `.venv/bin/python -m pytest -q`
Expected: tất cả PASS (22 test). Test cũ `test_fixed_chunk_overlaps_and_covers_text` vẫn PASS.

---

### Task 3: `src/generation/llm.py` — client LLM có cache

**Files:**
- Create: `src/generation/__init__.py` (rỗng)
- Create: `src/generation/llm.py`
- Modify: `.env.example`, `.gitignore`
- Test: `tests/test_llm.py`

**Interfaces:**
- Consumes: không phụ thuộc task trước.
- Produces (Sprint 3 agent và Sprint 4 judge dùng):
  - `class LLM(client, model: str, cache_dir=Path(".cache/llm"))`, thuộc tính `calls: int` (số lượt gọi API thật, không tính cache).
  - `LLM.chat(messages: list[dict], temperature=0.0, **params) -> str`
  - `LLM.chat_json(messages: list[dict], **params) -> dict`, ném `ValueError` nếu 2 lần đều không ra JSON object.
  - `parse_json(text: str | None) -> dict | None`
  - `from_env(prefix="LLM", cache_dir=Path(".cache/llm")) -> LLM`; đọc `<prefix>_BASE_URL`, `<prefix>_API_KEY`, `<prefix>_MODEL`, tùy chọn `<prefix>_MAX_RETRIES` (mặc định 8); `prefix="JUDGE"` cho bộ chấm. Ném `RuntimeError` liệt kê biến thiếu.

- [ ] **Step 1: Viết test thất bại**

Tạo `tests/test_llm.py`:

```python
import os
from types import SimpleNamespace

import pytest

from src.generation.llm import LLM, from_env, parse_json

MSG = [{"role": "user", "content": "Xin chào"}]


class FakeClient:
    """Giả lập client openai: trả lần lượt các reply, ghi lại request."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        content = self.replies.pop(0)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def test_second_identical_call_is_served_from_cache(tmp_path):
    client = FakeClient(["chào bạn"])
    llm = LLM(client, "m", tmp_path)
    assert llm.chat(MSG) == "chào bạn"
    assert llm.chat(MSG) == "chào bạn"
    assert llm.calls == 1
    assert len(client.requests) == 1


def test_cache_survives_new_instance(tmp_path):
    LLM(FakeClient(["a"]), "m", tmp_path).chat(MSG)
    llm2 = LLM(FakeClient([]), "m", tmp_path)
    assert llm2.chat(MSG) == "a"
    assert llm2.calls == 0


def test_different_model_or_params_miss_cache(tmp_path):
    client = FakeClient(["a", "b", "c"])
    LLM(client, "m1", tmp_path).chat(MSG)
    LLM(client, "m2", tmp_path).chat(MSG)
    LLM(client, "m1", tmp_path).chat(MSG, temperature=0.7)
    assert len(client.requests) == 3


def test_request_uses_model_and_temperature_zero_by_default(tmp_path):
    client = FakeClient(["a"])
    LLM(client, "gemini-x", tmp_path).chat(MSG)
    assert client.requests[0] == {"model": "gemini-x", "messages": MSG, "temperature": 0.0}


def test_empty_reply_is_not_cached(tmp_path):
    client = FakeClient([None, "ok"])
    llm = LLM(client, "m", tmp_path)
    assert llm.chat(MSG) == ""
    assert llm.chat(MSG) == "ok"
    assert llm.calls == 2


def test_corrupted_cache_file_is_refetched(tmp_path):
    llm = LLM(FakeClient(["a", "b"]), "m", tmp_path)
    llm.chat(MSG)
    next(tmp_path.glob("*.json")).write_text("{hỏng", encoding="utf-8")
    assert llm.chat(MSG) == "b"


@pytest.mark.parametrize("text", ['{"a": 1}', '```json\n{"a": 1}\n```', 'Kết quả:\n{"a": 1}\nHết.'])
def test_parse_json_tolerates_fences_and_prose(text):
    assert parse_json(text) == {"a": 1}


@pytest.mark.parametrize("text", ["", "không có json", "[1, 2]", "{sai cú pháp}", None])
def test_parse_json_returns_none_for_non_object(text):
    assert parse_json(text) is None


def test_chat_json_retries_once_with_hint(tmp_path):
    client = FakeClient(["xin lỗi, tôi không chắc", '{"type": "direct"}'])
    assert LLM(client, "m", tmp_path).chat_json(MSG) == {"type": "direct"}
    assert "JSON" in client.requests[1]["messages"][-1]["content"]


def test_chat_json_raises_after_second_failure(tmp_path):
    with pytest.raises(ValueError):
        LLM(FakeClient(["không", "vẫn không"]), "m", tmp_path).chat_json(MSG)


def test_from_env_builds_client_with_retries(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # không có .env
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("LLM_API_KEY", "k")
    monkeypatch.setenv("LLM_MODEL", "m")
    monkeypatch.delenv("LLM_MAX_RETRIES", raising=False)
    llm = from_env()
    assert llm.model == "m"
    assert llm.client.max_retries == 8
    assert str(llm.client.base_url).startswith("https://example.com/v1")


def test_from_env_reports_missing_variables(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for key in ("JUDGE_BASE_URL", "JUDGE_API_KEY", "JUDGE_MODEL"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(RuntimeError, match="JUDGE_API_KEY"):
        from_env("JUDGE")


def test_from_env_reads_dotenv_without_overriding_shell(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "# ghi chú\nLLM_BASE_URL=https://file.example/v1\nLLM_API_KEY='k-file'\nLLM_MODEL=from-file\n",
        encoding="utf-8",
    )
    # os.environ riêng cho test: biến do .env nạp vào không rò sang test khác
    monkeypatch.setattr(os, "environ", {"LLM_MODEL": "from-shell"})
    llm = from_env()
    assert llm.model == "from-shell"
    assert llm.client.api_key == "k-file"
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `.venv/bin/python -m pytest -q tests/test_llm.py`
Expected: collection error `ModuleNotFoundError: No module named 'src.generation'` (hoặc `...llm`).

- [ ] **Step 3: Cài đặt**

Đảm bảo thư viện đã cài: `.venv/bin/pip install -q -r requirements.txt`.

Tạo `src/generation/__init__.py` rỗng. Tạo `src/generation/llm.py`:

```python
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
        params = {"temperature": temperature, **params}
        path = self._cache_path(messages, params)
        try:
            return json.loads(path.read_text(encoding="utf-8"))["content"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass  # chưa có hoặc file cache hỏng: gọi API
        resp = self.client.chat.completions.create(model=self.model, messages=messages, **params)
        self.calls += 1
        content = resp.choices[0].message.content or ""
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
```

Thay toàn bộ nội dung `.env.example` bằng:

```
# LLM cho tác tử (API chuẩn OpenAI).
# Gemini: LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=

# LLM cho bộ chấm, nên khác nhà cung cấp với tác tử.
# Groq: JUDGE_BASE_URL=https://api.groq.com/openai/v1
JUDGE_BASE_URL=
JUDGE_API_KEY=
JUDGE_MODEL=

# Embedding mặc định BAAI/bge-m3 chạy local. Bỏ comment 2 dòng dưới để dùng OpenAI.
# EMBED_MODEL=text-embedding-3-small
# OPENAI_API_KEY=
```

Thêm một dòng vào cuối `.gitignore`:

```
.cache/
```

- [ ] **Step 4: Chạy toàn bộ test**

Run: `.venv/bin/python -m pytest -q`
Expected: tất cả PASS (41 test).

---

### Task 4: Gọi thử API thật và cập nhật PLAN

Không có test tự động (cần key thật); đây là bước nghiệm thu thủ công của mục "đăng ký API key" trong `docs/PLAN.md`.

**Files:**
- Create (không commit, đã bị `.gitignore`): `.env`
- Modify: `docs/PLAN.md` (đánh dấu `[x]`)

**Interfaces:**
- Consumes: `from_env` từ Task 3.

- [ ] **Step 1: Lấy key và điền `.env`**

Lấy key Gemini tại aistudio.google.com và key Groq tại console.groq.com. `cp .env.example .env`, điền `LLM_*` (Gemini) và `JUDGE_*` (Groq). Tên model lấy từ trang danh sách model của từng nhà cung cấp (chọn model Flash của Gemini; model Llama/Qwen cỡ lớn nhất của Groq).

- [ ] **Step 2: Gọi thử mỗi bên một lần**

Run:

```bash
.venv/bin/python -c "
from src.generation.llm import from_env
for p in ('LLM', 'JUDGE'):
    llm = from_env(p)
    print(p, llm.model, '->', llm.chat([{'role': 'user', 'content': 'Trả lời đúng một từ: Xin chào'}]))
    print(p, 'json ->', llm.chat_json([{'role': 'user', 'content': 'Trả về JSON {\"ok\": true}'}]))
"
```

Expected: mỗi bên in một câu chào và `{'ok': True}`. Chạy lại lệnh lần hai: kết quả giống hệt và không tốn quota (lấy từ `.cache/llm/`). Nếu lỗi 400 về tham số `temperature` hay URL: sửa `.env`, không sửa code.

- [ ] **Step 3: Cập nhật `docs/PLAN.md`**

Đánh dấu `[x]` cho 4 mục Sprint 1 của Đạt: "Bổ sung trường expiry_date", "fixed_chunk ghi danh sách các Điều", "src/generation/llm.py", "Cập nhật .env.example". Sửa tương ứng trong Phụ lục B của `Đề cương DACNTT.txt`.

Các mục còn lại của Đạt trong Sprint 1 (chạy chunker trên 5 file thật, sửa case lỗi, chạy index với BGE-M3) phụ thuộc file của Hùng; làm khi có dữ liệu.
