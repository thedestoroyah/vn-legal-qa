# Bàn giao phiên làm việc (cập nhật 2026-10-16, cuối phiên)

> Dán file này (hoặc bảo Claude đọc `docs/HANDOFF.md`) vào phiên mới. Sau đó đọc theo thứ tự ở mục "Đọc gì trước".

## 1. Dự án

Đề tài DACNTT (TDTU, HK7): hệ thống hỏi đáp pháp luật tiếng Việt dựa trên **Agentic-RAG** có truy xuất căn cứ **theo hiệu lực tại thời điểm tình huống** và **kiểm chứng trích dẫn**. Hạn nộp **23:59 21/11/2026**. Nhóm 2 người, repo `github.com/TheDestoroyah/vn-legal-qa`.

- **Phạm Huỳnh Quốc Đạt** (người dùng): lõi kỹ thuật (chunking, truy xuất, tác tử, API, đánh giá). Dùng Claude Code.
- **Hoàng Sinh Hùng**: dữ liệu luật, tập kiểm thử, giao diện Streamlit, viết báo cáo. Chỉ dùng web chat và agent CLI free tier, Windows PowerShell. Plan của Hùng viết dạng thẻ việc tự chứa đủ thông tin.
- Người dùng **tự commit và tự push**; không tự ý commit. Giao tiếp tiếng Việt.
- **Quy tắc code (global, `~/.claude/rules/docstrings-comments.md`):** hàm/lớp quan trọng có docstring tiếng Việt (làm gì, đầu vào, đầu ra, ngoại lệ); comment vừa phải, giải thích "tại sao". Đã bổ sung cho `src/` và `eval/`; `data/` (file của Hùng) chưa sửa.

## 2. Đọc gì trước (theo thứ tự)

1. **`docs/superpowers/plans/2026-10-16-sprint3-dat.md`**: plan Sprint 3 của Đạt (8 task, TDD, đủ code mẫu). **Việc tiếp theo**: người dùng duyệt plan rồi chọn cách chạy (subagent-driven hoặc native).
2. `docs/sprints/2026-10-16-sprint3-hung.md`: 5 thẻ việc Sprint 3 của Hùng (H8–H12), cùng yêu cầu làm trước các thẻ Sprint 2 còn dở.
3. `docs/superpowers/specs/2026-10-09-agentic-legal-qa-design.md`: spec toàn dự án (đã duyệt; mục 5 là tác tử).
4. `Đề cương DACNTT.txt` (gốc repo): **Phụ lục A** = định dạng dữ liệu và API (A.5 là phản hồi tác tử); **Phụ lục B** = phân công theo sprint.
5. `docs/PLAN.md`: checklist theo sprint, đồng bộ với Phụ lục B (sửa một nơi thì sửa cả hai).
6. Tham khảo: `docs/superpowers/plans/2026-10-15-sprint2-dat.md` (Sprint 2 đã xong), `docs/sprints/2026-10-15-sprint2-hung.md` (H1–H7).

## 3. Các quyết định đã chốt (không brainstorm lại)

- **4 câu hỏi nghiên cứu:** RQ1 truy xuất (BM25 / Dense / Hybrid RRF / +rerank); RQ2 phân đoạn (fixed / Điều / Khoản / Khoản+tiêu đề, so ở cấp Điều); RQ3 Agentic-RAG (baseline / full / ablation no_router, no_grading, no_verify); RQ4 hiệu lực theo thời gian (có BLLĐ 2012 đã hết hiệu lực).
- **Tác tử** (LangGraph, đồ thị có kiểm soát, 3–8 lượt gọi LLM/câu): route → (lookup_article | retrieve → grade ⟲ ≤2 lần) → generate → verify. Không lọc theo lĩnh vực ở bước truy xuất. Chi tiết trong spec mục 5.
- **Corpus:** BLDS 2015, BLLĐ 2019, LDN 2020, LTM 2005 + BLLĐ 2012 (chỉ cho RQ4). Là **văn bản gốc, chưa hợp nhất sửa đổi** (ghi là giới hạn). Không có Nghị định/Thông tư.
- **Hiệu lực:** có hiệu lực tại ngày d khi `effective_date ≤ d < expiry_date`; `expiry_date = null` = còn hiệu lực; `date=None` khi truy xuất = chỉ lấy văn bản còn hiệu lực.
- **Tập kiểm thử ~170–180 câu từ 3 nguồn, báo cáo tách theo `source`:** `zalo` (~81 câu người viết, chỉ BLDS + LDN, căn cứ cấp Điều, bộ chính cho RQ1/RQ2); `synthetic` (65 câu do AI sinh trong `data/test_cases.json`, bộ phụ, kiểm định mẫu 20 câu); `manual` (~35 câu tự soạn: situational BLLĐ/LTM, temporal, direct, out_of_scope). **VLQA 2025 không dùng** (dữ liệu chưa công bố).
- **LLM:** API free tier qua giao diện chuẩn OpenAI, cache đĩa. Tác tử: **`gemini-3.1-flash-lite`** (15 RPM, 250k TPM, 500 RPD; đã gọi thử 16/10, ~1,2 s/lượt, JSON ổn). Judge: Groq (chưa có key, Sprint 4). Embedding BGE-M3 và reranker bge-reranker-v2-m3 chạy local CPU.
- **UI:** Streamlit + FastAPI, không SQLite, không hội thoại nhiều lượt.
- **Giới hạn Zalo:** chỉ gán nhãn cấp Điều, nên chỉ số cấp Khoản chỉ tính cho câu có gold cấp Khoản.

## 4. Trạng thái code (repo `vn-legal-qa/`, Python 3.14, venv `.venv/`) — cập nhật 16/10

**Sprint 2 phần Đạt: xong, đã commit** (3 commit `51d8cfe`, `8f58028`, `1868da0`; người dùng tự push). 112 test pass. Đã qua review độc lập (Opus), bảng RQ1/RQ2 chạy lại sau khi sửa.

- `src/ingestion/legal_chunker.py`: đọc `data/structured/*.json`, sinh `chunks.jsonl` (Khoản, 4167), `chunks_article.jsonl` (Điều, 1451), `chunks_fixed.jsonl` (1457). Số Điều khớp: LTM 324, BLLĐ 220, LDN 218, BLDS 689.
- `src/ingestion/index.py`: 4 biến thể `--variant clause_header|clause_plain|article|fixed`, mỗi biến thể một collection Chroma (`chroma_db/`, đã nạp đủ, bị ignore; mất 15–29 phút/biến thể trên CPU).
- `src/retrieval/`: `Retriever.search(query, k, date, mode)`, `get_article(law_id, number)` (trả chunk cấp Điều, `chunk_id` = khóa Điều), `load_retriever(variant)`; RRF k=60; rerank top-10.
- `src/generation/llm.py`: `LLM.chat`, `chat_json`, `from_env`. Các lỗi hoãn từ Sprint 1 sẽ sửa ở Sprint 3 Task 1.
- `eval/`: `import_cases.py` (146 câu hiện tại), `metrics.py`, `evaluate.py --rq rq1|rq2`, kết quả ở `eval/results/`.
- `.env` (bị ignore) đã có key Gemini, `LLM_BASE_URL`, `LLM_MODEL=gemini-3.1-flash-lite`. **Key từng nằm trong `.env.example`**, đã chuyển sang `.env` trước khi commit; `.env.example` không chứa key. Không in `.env` ra màn hình.
- `data/raw/laws.json`: **chưa có BLLĐ 2012**, chưa đối chiếu nguồn (việc của Hùng, H1–H2).
- Plan Sprint 3, thẻ Hùng Sprint 3, cập nhật PLAN/đề cương/spec/HANDOFF, `.env.example` đã commit (`docs:` commit cuối); người dùng tự push.

### Kết quả RQ1/RQ2 (n = 81 câu Zalo = bộ chính; 65 synthetic = bộ phụ)

Chỉ tiêu trên Zalo, `clause_header/hybrid_rerank`: **Hit@5 0,827 (≥ 0,80 đạt); Recall@10 0,866 (≥ 0,75 đạt)**.

| RQ1 (Zalo) | Hit@5 | Recall@10 | MRR@10 | DRM@5 |
|---|---|---|---|---|
| BM25 | 0,753 | 0,819 | 0,699 | 0,143 |
| Dense | 0,827 | 0,854 | 0,726 | 0,101 |
| Hybrid RRF | 0,815 | 0,866 | 0,717 | 0,104 |
| Hybrid + rerank | 0,827 | 0,866 | 0,785 | 0,084 |

| RQ2 (Zalo, hybrid_rerank) | Hit@5 | Recall@10 | MRR@10 | DRM@5 |
|---|---|---|---|---|
| fixed | 0,605 | 0,623 | 0,512 | 0,091 |
| article | 0,877 | 0,895 | 0,813 | 0,106 |
| clause_plain | 0,827 | 0,866 | 0,782 | 0,114 |
| clause_header | 0,827 | 0,866 | 0,785 | 0,084 |

Cách đọc (đừng nói quá): n = 81 nên 1 câu = 0,012; các chênh lệch ≤ 0,02 là nhiễu. Chắc chắn: rerank cải thiện MRR; cắt cố định kém rõ rệt; câu synthetic dễ hơn Zalo (BM25 Hit@5 0,954 vs 0,753, ủng hộ giả thuyết câu hỏi bám câu chữ điều luật). Cẩn thận: biến thể `article` được lợi vì nhãn Zalo cũng ở cấp Điều; Hybrid không hơn Dense về Hit@5 trên Zalo. Rerank vẫn ~5,3 s/câu trên CPU (> 3 s; `article` ~10,6 s).

## 5. Việc tiếp theo

1. Người dùng duyệt `docs/superpowers/plans/2026-10-16-sprint3-dat.md`, chọn cách chạy (Sprint 2 đã chạy native: Claude tự làm hết, cuối cùng một reviewer Opus độc lập; ledger trong `.superpowers/sdd/`). Plan ghi rõ số test kỳ vọng sau mỗi task (112 → 207).
2. Sau Task 7 có thể gọi thật: `python -m src.agent.run "câu hỏi" --config full`. Task 8 chạy `python -m eval.agent_smoke` (10 câu, ~5–8 phút, ~50 lượt gọi Gemini).
3. Chờ Hùng: thẻ Sprint 2 còn dở (H1, H2, H6 quan trọng nhất cho RQ3/RQ4), rồi H8–H12. Khi có BLLĐ 2012: chạy lại chunker, `index --variant clause_header --rebuild` (cần cho RQ4), `python -m eval.import_cases`.
4. Việc của Đạt còn dở: kiểm chéo căn cứ câu manual của Hùng; lấy key Groq (Sprint 4); gửi email tóm tắt đề cương cho thầy Lê Anh Cường.
5. Plan Sprint 4 (FastAPI, evaluate phần sinh, judge) viết ở đầu Sprint 4, dựa trên `Agent.run` thật.

## 6. Rủi ro, lưu ý, lỗi Minor còn hoãn

- **Minor từ review Sprint 2 (xử lý trước khi viết báo cáo):** (M1) Điều nằm trực tiếp dưới Phần (BLDS Điều 688–689) bị gán Chương của Phần trước; (M2) reranker `max_length=512` cắt Điều dài (139 Điều > 300 từ) → ảnh hưởng tính hợp lệ của biến thể `article`; (M3) `check_date` nhận cả ngày dạng tuần ISO; (M4) `manual_cases.json` không phải danh sách → traceback thô; (M5) JSON cấu trúc thiếu `law_number` làm sập cả lượt chunk, trùng số hiệu giữa file không bị phát hiện; (M6) câu Zalo nhiều luật lấy `domain` của luật đầu (`Z_40cab1ef`); (M7) cột `n` gây hiểu nhầm cho chỉ số Khoản; (M8) thiếu test biên giữa BM25 và Chroma, test lọc Chroma gõ lại `where` thay vì gọi `chroma_where`; (M9) README chưa liệt kê đủ 4 biến thể cần nạp cho rq2; (M10) `get_article` trả None trên biến thể `fixed`.
- **Quyết định đã ghi (Sprint 2):** `RERANK_TOP` 20 → 10 vì 11 s/câu; mỗi cửa sổ cố định chỉ tính Điều chiếm nhiều từ nhất (`main_article`) khi chấm cấp Điều; phần đuôi chưa rerank vẫn giữ theo thứ tự RRF để độ sâu bằng các chế độ khác.
- **Lỗi `llm.py` còn hoãn từ Sprint 1:** regex JSON tham lam, `chat_json` cache output hỏng, trùng file `.tmp` khi gọi song song, khóa cache thiếu `base_url`, `.env` tìm theo thư mục chạy lệnh. Đã đưa vào Sprint 3 Task 1.
- **Quota Gemini (rủi ro Sprint 4–5):** 500 lượt/ngày. RQ3 = 5 cấu hình × ~180 câu × ~4–5 lượt ≈ 4.000 lượt logic. Cache chia sẻ giữa các cấu hình (cùng prompt thì trúng cache), nhưng vẫn cần nhiều ngày chạy. Phương án: chạy ablation trên tập con 40–60 câu (spec mục 9), giữ cùng một model cho mọi cấu hình để so sánh công bằng. Tính lịch chạy trong plan Sprint 4.
- **Quyết định thiết kế tác tử (plan Sprint 3):** bằng chứng gộp qua các vòng viết lại (tối đa 15 đoạn); `no_verify` chỉ bỏ verify(b), verify(a) luôn chạy; câu trả lời không còn mã nào được ghi chú "chưa có căn cứ trích dẫn"; `llm_calls` trong trace đếm lượt gọi logic (kể cả cache) để số liệu RQ3 không phụ thuộc cache; ngày chỉ có năm → `YYYY-07-01`, có tháng → ngày 15.
- **Tài liệu tham khảo:** đã xác minh Pham et al. (KMIS 2025), Reuter et al. (NLLP 2025), VLQA (arXiv 2507.19995), Nguyen Ba et al. (arXiv 2409.13699). Chưa tra lại: số trang RAGAS, ALCE, RRF; danh sách tác giả BGE-M3; URL `challenge.zalo.ai`.
- BLLĐ 2012 (10/2012/QH13, 2013-05-01 → hết hiệu lực 2021-01-01) và ví dụ Q001 trong Phụ lục A là trí nhớ của Claude, chưa kiểm; Hùng kiểm ở H2.
