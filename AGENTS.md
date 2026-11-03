# vn-legal-qa: bối cảnh dự án cho người và agent

Đọc file này trước khi sửa code, dữ liệu hay tập kiểm thử. Chỉ ghi những thứ ít đổi; số liệu nằm trong `eval/results/`, lịch và việc cần làm nằm trong `docs/PLAN.md`.

## Đề tài

Đồ án CNTT ĐA127 (TDTU, HK7), GVHD PGS.TS. Lê Anh Cường. Hệ thống hỏi đáp pháp luật tiếng Việt dựa trên **Agentic-RAG**: truy xuất căn cứ **theo hiệu lực tại thời điểm sự việc** và **kiểm chứng trích dẫn**.

- **Hạn nộp: 23:59 04/12/2026.** Đóng băng tính năng 12/11 (sau đó chỉ sửa lỗi). Lịch sprint: `docs/PLAN.md`.
- Phạm Huỳnh Quốc Đạt (52300098): lõi kỹ thuật (truy xuất, tác tử, đánh giá).
- Hoàng Sinh Hùng (52300106): dữ liệu, tập kiểm thử, giao diện, báo cáo.

## Tài liệu chính

| File | Nội dung |
|---|---|
| `docs/managements/Đề cương DACNTT.md` | Đề cương (nguồn chính). Phụ lục A: định dạng dữ liệu, chunk, test case, API. Phụ lục B: phân công theo sprint |
| `docs/PLAN.md` | Checklist theo sprint, đồng bộ với Phụ lục B (sửa bên này thì sửa cả bên kia) |
| `docs/superpowers/specs/2026-10-09-agentic-legal-qa-design.md` | Thiết kế: RQ, tác tử, lỗi, cách đánh giá, rủi ro |
| `docs/superpowers/specs/2026-11-03-heldout-prereg.md` | Chốt trước tập giữ riêng 30 câu |
| `docs/rubric.md`, `docs/judge_review.md` | Thang chấm tay, nhận xét prompt chấm |
| `docs/sprints/`, `docs/superpowers/plans/` | Thẻ việc của Hùng, plan của Đạt theo sprint |
| `docs/report/` | Bản nháp các chương và file báo cáo |

## Kiến trúc

- **Corpus** (5 văn bản): BLDS 2015, BLLĐ 2019, LDN 2020, LTM 2005, BLLĐ 2012 (hết hiệu lực 01/01/2021, dùng cho RQ4). Văn bản gốc, chưa hợp nhất sửa đổi. Hiệu lực tại ngày d: `effective_date ≤ d < expiry_date`.
- **Chunk**: mã dạng `BLLD2019_Dieu20_Khoan1`. 4 biến thể: `clause_header` (mặc định), `clause_plain`, `article`, `fixed`. Index: ChromaDB (`chroma_db/`, không commit), embedding BGE-M3 local, reranker local.
- **Truy xuất**: BM25 + dense, gộp bằng RRF, rerank; lọc theo ngày hiệu lực.
- **Tác tử** (LangGraph, `src/agent/`): route → (lookup_article | retrieve → grade, lặp tối đa 2 lần) → generate → verify. verify (a): regex gỡ mã nằm ngoài ngữ cảnh; verify (b): 1 lượt LLM kiểm từng cặp câu–đoạn. Một đồ thị dùng chung cho 5 cấu hình (bật/tắt bằng cờ).
- **LLM**: tác tử dùng Gemini `gemini-3.1-flash-lite` (free tier 500 lượt/ngày/key); bộ chấm dùng Groq `openai/gpt-oss-120b` (khoảng 100 lượt chấm/ngày/key). Mọi cấu hình phải dùng cùng model. Có cache LLM trên đĩa: đầu vào trùng khớp thì không tốn quota.
- **API**: FastAPI `src/api/main.py` (`/api/ask`, `/api/article`). **Giao diện**: NiceGUI `src/ui/web/` (chính), Streamlit `src/ui/app.py`.

## Câu hỏi nghiên cứu

- **RQ1** truy xuất: BM25 / Dense / Hybrid RRF / Hybrid + rerank, trên 77 câu Zalo, đo ở cấp Điều.
- **RQ2** phân đoạn: fixed / Điều / Khoản / Khoản + tiêu đề.
- **RQ3** tác tử: `baseline`, `full`, `no_router`, `no_grading`, `no_verify`.
- **RQ4** hiệu lực (chỉ câu `temporal`): `event` (lọc theo ngày sự việc), `current` (chỉ văn bản còn hiệu lực), `any` (không lọc).
- So sánh ghép cặp theo câu, bootstrap 95% (`report --ci`).

## Tập kiểm thử (đọc kỹ trước khi sửa)

- `eval/test_cases.json` (209 câu) **sinh tự động** bằng `python -m eval.import_cases`; không sửa tay. Câu tự soạn sửa trong `eval/manual_cases.json` rồi chạy lại lệnh trên.
- Nguồn: zalo 77 (gold cấp Điều, không có đáp án mẫu), synthetic 65, manual 67 (situational 15, temporal 32, direct 15, out_of_scope 5).
- **Tập giữ riêng M_038–M_067** đã chốt trước và đã chạy: không sửa, không xóa, trừ lỗi gõ nhầm mã căn cứ (khi đó phải ghi vào báo cáo).
- Danh sách mẫu cố định trong `eval/results/`: `subset_rq3_60.json`, `subset_rq3_30.json`, `subset_rq4_20.json`. Không xóa, không tạo lại.
- **Sửa câu hỏi hoặc đáp án của một câu đã chạy** thì kết quả cũ không còn đúng. Phải xóa các dòng có id đó trong `eval/results/agent_rq3*.jsonl`, `agent_rq4*.jsonl` (cả file `_judge`), rồi chạy lại `run`, `judge`, `report`. Báo Đạt trước vì việc này tốn quota.
- **Sửa prompt** trong `src/generation/` hoặc `src/agent/` làm mọi kết quả RQ3/RQ4 mất hiệu lực. Không sửa nếu chưa thống nhất với Đạt.

## Lệnh thường dùng

```bash
pip install -r requirements.txt            # cài torch bản CPU trước, xem README
pytest -q                                  # phải pass hết trước khi commit
python -m src.ingestion.legal_chunker      # văn bản -> data/processed/*.jsonl
python -m src.ingestion.index --variant clause_header --rebuild
python -m eval.import_cases                # manual + zalo + synthetic -> eval/test_cases.json
python -m eval.evaluate --rq rq1           # RQ1/RQ2, chạy CPU, không tốn quota
python -m eval.agent_eval run --rq rq3 --configs full     # RQ3/RQ4: xem docstring eval/agent_eval.py
python -m eval.agent_eval judge --rq rq3
python -m eval.agent_eval report --rq rq3 --common --ci --out eval/results/<tên>.md
uvicorn src.api.main:app --port 8000       # backend
python -m src.ui.web.main                  # giao diện NiceGUI, http://127.0.0.1:8080
```

Biến môi trường: xem `.env.example`. Không commit `.env`, không dán key vào chat hay log.

## Quy ước

- Docstring và comment **tiếng Việt**; tên biến, hàm, lớp tiếng Anh. Hàm công khai có docstring (làm gì, đầu vào, đầu ra, ngoại lệ). Comment giải thích "tại sao", không dịch lại code.
- Commit: `<type>: <mô tả>`, với type là feat, fix, refactor, docs, test, chore, data. Mỗi commit một việc. Không commit `chroma_db/`, `.cache/`, `.venv/`.
- Sửa code thì thêm hoặc sửa test trong `tests/`. Đừng sửa test cho pass nếu chưa hiểu vì sao test hỏng; nhiều test giữ một quyết định thiết kế (ví dụ `test_reindex_without_rebuild_clears_stale_fields`).
- Sửa định dạng dữ liệu hoặc API thì sửa cả Phụ lục A trong đề cương.
- Số liệu trong báo cáo lấy từ `eval/results/*.md`, không chép tay từ chat.
