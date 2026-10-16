"""LLM và Retriever giả cho test tác tử: LLM thật (cache, chat_json) trên client trả lời theo từng nút."""
import json
import re
from types import SimpleNamespace

from src.agent.nodes import Deps
from src.generation.llm import LLM
from src.generation.prompts import ROLES

LAWS = {
    "BLDS2015": {"document": "Bộ luật Dân sự 2015", "effective_date": "2017-01-01", "expiry_date": None},
    "BLLD2012": {"document": "Bộ luật Lao động 2012", "effective_date": "2013-05-01", "expiry_date": "2021-01-01"},
    "BLLD2019": {"document": "Bộ luật Lao động 2019", "effective_date": "2021-01-01", "expiry_date": None},
}


def node_of(messages):
    """Tên nút đang gọi LLM, nhận ra qua câu vai trò đầu system prompt."""
    system = messages[0]["content"]
    return next(name for name, role in ROLES.items() if system.startswith(role))


class ScriptedClient:
    """Client openai giả: mỗi nút có danh sách trả lời riêng, lấy lần lượt; nút gọi ngoài kịch bản thì KeyError."""

    def __init__(self, **replies):
        self.replies = {node: list(items) for node, items in replies.items()}
        self.seen = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, model, messages, **params):
        node = node_of(messages)
        self.seen.append((node, messages))
        reply = self.replies[node].pop(0)
        content = reply if isinstance(reply, str) else json.dumps(reply, ensure_ascii=False)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


def make_llm(tmp_path, **replies):
    return LLM(ScriptedClient(**replies), "fake", tmp_path)


def nodes_called(llm):
    return [node for node, _ in llm.client.seen]


def chunk(cid, content="nội dung"):
    m = re.fullmatch(r"([A-Z]+\d{4})_Dieu(\w+?)(?:_Khoan(\d+))?", cid)
    return {"chunk_id": cid, "law_id": m[1], "document": f"Văn bản {m[1]}", "article": f"Điều {m[2]}",
            "article_title": "Tiêu đề", "clause": f"Khoản {m[3]}" if m[3] else None, "content": content, "score": 0.5}


class FakeRetriever:
    """Mỗi lượt search lấy danh sách kế tiếp trong `results` (hết thì trả rỗng); get_article tra trong `articles`."""

    def __init__(self, results=(), articles=None):
        self.results = list(results)
        self.articles = articles or {}
        self.searches, self.lookups = [], []

    def search(self, query, k=5, date=None, mode="hybrid_rerank"):
        self.searches.append({"query": query, "k": k, "date": date})
        return self.results.pop(0) if self.results else []

    def get_article(self, law_id, number):
        self.lookups.append((law_id, number))
        return self.articles.get(f"{law_id}_Dieu{number}")


def make_deps(tmp_path, retriever=None, **replies):
    return Deps(make_llm(tmp_path, **replies), retriever or FakeRetriever(), LAWS)
