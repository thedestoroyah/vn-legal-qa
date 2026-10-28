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

# data/structured/*.json (Hùng tạo bằng MinerU + data/legal_structure_parser.py) phải có số hiệu trong data/raw/laws.json
python -m src.ingestion.legal_chunker                # -> data/processed/chunks.jsonl, chunks_article.jsonl, chunks_fixed.jsonl
python -m src.ingestion.index --variant clause_header --rebuild --query "lãi chậm trả tiền"
python -m eval.import_cases                          # -> eval/test_cases.json
python -m eval.evaluate --rq rq1                     # -> eval/results/retrieval_rq1.md
python -m src.agent.run "Bên mua trả tiền chậm có phải trả lãi không?"   # hỏi tác tử từ dòng lệnh
uvicorn src.api.main:app --port 8000                                   # API cho giao diện (Phụ lục A.5)
python -m eval.agent_eval run --rq rq3 --configs full --limit 10       # RQ3/RQ4: xem docstring eval/agent_eval.py
pytest
```
Embedding mặc định là `BAAI/bge-m3` (chạy local, ~2.3GB lần đầu). Đặt `EMBED_MODEL=text-embedding-3-small` để dùng OpenAI.

torch nên cài bản CPU trước: `pip install torch --index-url https://download.pytorch.org/whl/cpu`. Định dạng dữ liệu: Phụ lục A trong đề cương. Kế hoạch chi tiết: [docs/PLAN.md](docs/PLAN.md).
