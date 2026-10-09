# vn-legal-qa

Hệ thống hỏi đáp pháp luật tiếng Việt: truy xuất căn cứ pháp lý (BM25 + dense + reranker) và sinh câu trả lời kèm trích dẫn Điều/Khoản.

Dự án CNTT 2026–2027 — TDTU.

## Cấu trúc
- `data/` văn bản luật thô và chunks
- `src/ingestion` legal chunker, nạp vector DB
- `src/retrieval` BM25, dense, hybrid, reranker
- `src/generation` prompt, citation parser
- `src/api` FastAPI (`/api/ask`)
- `src/ui` Streamlit
- `eval/` test_cases.json, evaluate.py
