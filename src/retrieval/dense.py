"""Tìm kiếm ngữ nghĩa trên collection Chroma, lọc theo khoảng hiệu lực."""
from src.retrieval.filters import chroma_where


class DenseIndex:
    def __init__(self, collection, embed):
        self.collection, self.embed = collection, embed

    def search(self, query, k=50, date=None):
        res = self.collection.query(query_embeddings=self.embed([query]), n_results=k, where=chroma_where(date))
        # collection dùng khoảng cách cosine: 1 - khoảng cách = độ tương đồng
        return [(cid, 1.0 - dist) for cid, dist in zip(res["ids"][0], res["distances"][0])]
