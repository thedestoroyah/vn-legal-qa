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

## Cài đặt và chạy
```bash
python -m venv .venv && source .venv/bin/activate   # fish: source .venv/bin/activate.fish
pip install -r requirements.txt
cp .env.example .env                                # điền OPENAI_API_KEY nếu dùng OpenAI

# 1. Đặt data/raw/<LAW_ID>.md cho từng luật khai báo trong data/raw/laws.json
python -m src.ingestion.legal_chunker --fixed       # -> data/processed/chunks.jsonl (+ chunks_fixed.jsonl)
python -m src.ingestion.index --rebuild --query "lãi chậm trả tiền"
pytest
```
Embedding mặc định là `BAAI/bge-m3` (chạy local, ~2.3GB lần đầu). Đặt `EMBED_MODEL=text-embedding-3-small` để dùng OpenAI.

Định dạng file raw: Chương/Mục/Điều mỗi cái một dòng riêng, khoản dạng `1.`, điểm dạng `a)`. Kế hoạch chi tiết: [docs/PLAN.md](docs/PLAN.md).
