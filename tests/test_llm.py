import os
from types import SimpleNamespace

import pytest

from src.generation import llm as llm_module
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


@pytest.mark.parametrize("text, expected", [
    ('{"a": 1}', {"a": 1}),
    ('```json\n{"a": 1}\n```', {"a": 1}),
    ('Kết quả:\n{"a": 1}\nHết.', {"a": 1}),
    ('{"a": 1} và {"b": 2}', {"a": 1}),
    ('Ví dụ {x} rồi {"a": 1}', {"a": 1}),
])
def test_parse_json_tolerates_fences_and_prose(text, expected):
    assert parse_json(text) == expected


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
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("LLM_API_KEY", "k")
    monkeypatch.setenv("LLM_MODEL", "m")
    monkeypatch.setenv("LLM_MIN_INTERVAL", "4.2")
    monkeypatch.delenv("LLM_MAX_RETRIES", raising=False)
    llm = from_env(env_path=tmp_path / ".env")
    assert llm.model == "m"
    assert llm.client.max_retries == 8
    assert str(llm.client.base_url).startswith("https://example.com/v1")
    assert llm.min_interval == 4.2
    assert llm.base_url == "https://example.com/v1"


def test_from_env_reports_missing_variables(monkeypatch, tmp_path):
    for key in ("JUDGE_BASE_URL", "JUDGE_API_KEY", "JUDGE_MODEL"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(RuntimeError, match="JUDGE_API_KEY"):
        from_env("JUDGE", env_path=tmp_path / ".env")


def test_from_env_reads_dotenv_without_overriding_shell(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text(
        "# ghi chú\nLLM_BASE_URL=https://file.example/v1\nLLM_API_KEY='k-file'\nLLM_MODEL=from-file\n",
        encoding="utf-8",
    )
    # os.environ riêng cho test: biến do .env nạp vào không rò sang test khác
    monkeypatch.setattr(os, "environ", {"LLM_MODEL": "from-shell"})
    llm = from_env(env_path=tmp_path / ".env")
    assert llm.model == "from-shell"
    assert llm.client.api_key == "k-file"


def test_reply_without_choices_counts_as_empty(tmp_path):
    client = FakeClient([])
    client.chat.completions.create = lambda **kwargs: SimpleNamespace(choices=[])
    llm = LLM(client, "m", tmp_path)
    assert llm.chat(MSG) == ""
    with pytest.raises(ValueError):
        llm.chat_json(MSG)


def test_cache_key_includes_base_url(tmp_path):
    client = FakeClient(["a", "b"])
    LLM(client, "m", tmp_path, base_url="https://a/v1").chat(MSG)
    LLM(client, "m", tmp_path, base_url="https://b/v1").chat(MSG)
    assert len(client.requests) == 2


def test_requests_counts_cache_hits_but_calls_does_not(tmp_path):
    llm = LLM(FakeClient(["a"]), "m", tmp_path)
    llm.chat(MSG)
    llm.chat(MSG)
    assert (llm.requests, llm.calls) == (2, 1)


def test_min_interval_spaces_real_calls(tmp_path, monkeypatch):
    sleeps = []
    monkeypatch.setattr(llm_module.time, "sleep", sleeps.append)
    llm = LLM(FakeClient(["a", "b"]), "m", tmp_path, min_interval=10)
    llm.chat(MSG)
    llm.chat([{"role": "user", "content": "câu khác"}])
    assert len(sleeps) == 1 and 9 < sleeps[0] <= 10


def test_cache_hit_is_not_throttled(tmp_path, monkeypatch):
    sleeps = []
    monkeypatch.setattr(llm_module.time, "sleep", sleeps.append)
    llm = LLM(FakeClient(["a"]), "m", tmp_path, min_interval=10)
    llm.chat(MSG)
    llm.chat(MSG)
    assert sleeps == []


def test_chat_json_drops_broken_cache_entry(tmp_path):
    client = FakeClient(["không phải json", '{"a": 1}', "lần sau"])
    llm = LLM(client, "m", tmp_path)
    assert llm.chat_json(MSG) == {"a": 1}
    assert llm.chat(MSG) == "lần sau"  # bản hỏng đã bị xóa nên lần này gọi lại API


def test_env_path_is_repo_root():
    assert llm_module.ENV_PATH == llm_module.ROOT / ".env"
    assert (llm_module.ROOT / "requirements.txt").exists()


def test_waited_accumulates_throttle_sleep(tmp_path, monkeypatch):
    monkeypatch.setattr(llm_module.time, "sleep", lambda s: None)
    llm = LLM(FakeClient(["a", "b"]), "m", tmp_path, min_interval=10)
    llm.chat(MSG)
    llm.chat([{"role": "user", "content": "câu khác"}])
    assert 9 < llm.waited <= 10


def test_from_env_max_retries_argument_overrides_env(monkeypatch, tmp_path):
    for k, v in {"LLM_BASE_URL": "https://example.com/v1", "LLM_API_KEY": "k", "LLM_MODEL": "m",
                 "LLM_MAX_RETRIES": "8"}.items():
        monkeypatch.setenv(k, v)
    assert from_env(env_path=tmp_path / ".env", max_retries=2).client.max_retries == 2


def test_from_env_timeout_argument_sets_client_timeout(monkeypatch, tmp_path):
    for k, v in {"LLM_BASE_URL": "https://example.com/v1", "LLM_API_KEY": "k", "LLM_MODEL": "m"}.items():
        monkeypatch.setenv(k, v)
    assert from_env(env_path=tmp_path / ".env", timeout=30).client.timeout == 30
