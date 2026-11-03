import threading
import time

import httpx
import openai
import pytest
from fastapi.testclient import TestClient

from src.agent.run import Agent
from src.api.main import LLM_ERROR, MAX_QUESTION, create_app
from tests.agent_fakes import FakeRetriever, chunk, make_deps

A = "BLDS2015_Dieu357_Khoan1"
SIT = {"type": "situational", "event_date": None, "law_id": None, "article": None}


def real_agent(tmp_path, n=1):
    r = FakeRetriever([[chunk(A)]] * n, articles={"BLDS2015_Dieu357": chunk("BLDS2015_Dieu357")})
    return Agent(make_deps(tmp_path, r, route=[SIT] * n, grade=[{"sufficient": True, "new_query": None}] * n,
                           generate=[f"Có [{A}]."] * n, verify=[{"unsupported": []}] * n))


def client_for(agent):
    return TestClient(create_app(lambda: agent))


def test_ask_returns_api_shape(tmp_path):
    with client_for(real_agent(tmp_path)) as client:
        r = client.post("/api/ask", json={"question": "Chậm trả có phải trả lãi?"})
    assert r.status_code == 200
    assert set(r.json()) == {"answer", "refused", "citations", "retrieved_chunks", "trace"}
    assert r.json()["citations"][0]["chunk_id"] == A


@pytest.mark.parametrize("body", [{"question": ""}, {"question": "   "}, {"question": "x" * (MAX_QUESTION + 1)},
                                  {"question": "q", "config": "khác"}, {}])
def test_ask_rejects_bad_input_with_422(tmp_path, body):
    with client_for(real_agent(tmp_path)) as client:
        assert client.post("/api/ask", json=body).status_code == 422


class BrokenAgent:
    def __init__(self, error):
        self.error = error

    def run(self, question, config="full"):
        raise self.error


def test_llm_failure_returns_503_with_friendly_message():
    error = openai.APIConnectionError(request=httpx.Request("POST", "http://test"))
    with client_for(BrokenAgent(error)) as client:
        r = client.post("/api/ask", json={"question": "q"})
    assert r.status_code == 503 and r.json() == {"detail": LLM_ERROR}


class SlowAgent:
    """Ghi số lượt chạy đồng thời lớn nhất."""

    def __init__(self):
        self.active = self.peak = 0

    def run(self, question, config="full"):
        self.active += 1
        self.peak = max(self.peak, self.active)
        time.sleep(0.05)
        self.active -= 1
        return {"answer": "", "refused": True, "citations": [], "retrieved_chunks": [], "trace": []}


def test_ask_serializes_concurrent_requests():
    agent = SlowAgent()
    with client_for(agent) as client:
        threads = [threading.Thread(target=client.post, args=("/api/ask",), kwargs={"json": {"question": "q"}})
                   for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    assert agent.peak == 1


def test_article_found_and_missing(tmp_path):
    with client_for(real_agent(tmp_path)) as client:
        ok = client.get("/api/article/BLDS2015/357")
        missing = client.get("/api/article/BLDS2015/9999")
    assert ok.status_code == 200 and ok.json()["chunk_id"] == "BLDS2015_Dieu357"
    assert missing.status_code == 404


def test_health_reports_model(tmp_path):
    with client_for(real_agent(tmp_path)) as client:
        assert client.get("/health").json() == {"status": "ok", "model": "fake"}


def test_real_agent_loader_uses_few_retries(monkeypatch):
    seen = {}
    monkeypatch.setattr("src.agent.run.load_agent", lambda **kw: seen.update(kw) or "agent")
    from src.api import main
    assert main._load_real_agent() == "agent"
    assert seen["max_retries"] == main.API_LLM_MAX_RETRIES == 2
    assert seen["timeout"] == main.API_LLM_TIMEOUT == 30
