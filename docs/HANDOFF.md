# Bàn giao phiên làm việc (cập nhật 2026-10-15)

> Dán file này (hoặc bảo Claude đọc `docs/HANDOFF.md`) vào phiên mới. Sau đó đọc theo thứ tự ở mục "Đọc gì trước".

## 1. Dự án

Đề tài DACNTT (TDTU, HK7): hệ thống hỏi đáp pháp luật tiếng Việt dựa trên **Agentic-RAG** có truy xuất căn cứ **theo hiệu lực tại thời điểm tình huống** và **kiểm chứng trích dẫn**. Hạn nộp **23:59 21/11/2026**. Nhóm 2 người, repo `github.com/TheDestoroyah/vn-legal-qa`.

- **Phạm Huỳnh Quốc Đạt** (người dùng): lõi kỹ thuật (chunking, truy xuất, tác tử, API, đánh giá). Dùng Claude Code.
- **Hoàng Sinh Hùng**: dữ liệu luật, tập kiểm thử, giao diện Streamlit, viết báo cáo. Chỉ dùng web chat và agent CLI free tier, Windows PowerShell. Plan của Hùng viết dạng thẻ việc tự chứa đủ thông tin.
- Người dùng **tự commit và tự push**; không tự ý commit. Giao tiếp tiếng Việt.

## 2. Đọc gì trước (theo thứ tự)

1. `Đề cương DACNTT.txt` (thư mục gốc repo): đề cương đã viết lại. **Phụ lục A** = định dạng dữ liệu chuẩn; **Phụ lục B** = phân công theo sprint.
2. `docs/superpowers/specs/2026-10-09-agentic-legal-qa-design.md`: spec thiết kế toàn dự án (đã duyệt).
3. `docs/superpowers/plans/2026-10-15-sprint2-dat.md`: plan Sprint 2 của Đạt (8 task, TDD, đủ code mẫu). **Việc tiếp theo.**
4. `docs/sprints/2026-10-15-sprint2-hung.md`: 7 thẻ việc của Hùng (H1–H7).
5. `docs/PLAN.md`: checklist theo sprint, đồng bộ với Phụ lục B (sửa một nơi thì sửa cả hai).
6. `docs/superpowers/plans/2026-10-09-sprint1-core.md`: plan Sprint 1 đã làm xong (tham khảo).

## 3. Các quyết định đã chốt (không brainstorm lại)

- **4 câu hỏi nghiên cứu:** RQ1 truy xuất (BM25 / Dense / Hybrid RRF / +rerank); RQ2 phân đoạn (fixed / Điều / Khoản / Khoản+tiêu đề, so ở cấp Điều); RQ3 Agentic-RAG (baseline / full / ablation no_router, no_grading, no_verify); RQ4 hiệu lực theo thời gian (có BLLĐ 2012 đã hết hiệu lực).
- **Tác tử** (LangGraph, đồ thị có kiểm soát, 3–8 lượt gọi LLM/câu): route → (lookup_article | retrieve → grade ⟲ ≤2 lần) → generate → verify. Không lọc theo lĩnh vực ở bước truy xuất. Chi tiết trong spec mục 5.
- **Corpus:** BLDS 2015, BLLĐ 2019, LDN 2020, LTM 2005 + BLLĐ 2012 (chỉ cho RQ4). Là **văn bản gốc, chưa hợp nhất sửa đổi** (ghi là giới hạn). Không có Nghị định/Thông tư.
- **Hiệu lực:** có hiệu lực tại ngày d khi `effective_date ≤ d < expiry_date`; `expiry_date = null` = còn hiệu lực; `date=None` khi truy xuất = chỉ lấy văn bản còn hiệu lực.
- **Tập kiểm thử ~170–180 câu từ 3 nguồn, báo cáo tách theo `source`:** `zalo` (~81 câu người viết, chỉ BLDS + LDN, căn cứ cấp Điều, bộ chính cho RQ1/RQ2); `synthetic` (65 câu do AI sinh trong `data/test_cases.json`, bộ phụ, kiểm định mẫu 20 câu); `manual` (~35 câu tự soạn: situational BLLĐ/LTM, temporal, direct, out_of_scope). **VLQA 2025 không dùng** (dữ liệu chưa công bố).
- **LLM:** API free tier (Gemini cho tác tử, Groq cho judge) qua giao diện chuẩn OpenAI, cache đĩa. Embedding BGE-M3 và reranker bge-reranker-v2-m3 chạy local CPU.
- **UI:** Streamlit + FastAPI, không SQLite, không hội thoại nhiều lượt.
- **Giới hạn Zalo:** chỉ gán nhãn cấp Điều, nên chỉ số cấp Khoản chỉ tính cho câu có gold cấp Khoản.

## 4. Trạng thái code (repo `vn-legal-qa/`, Python 3.14, venv `.venv/`)

Đã có và test pass (44 test lúc cuối Sprint 1):

- `src/ingestion/legal_chunker.py`: **hiện vẫn là bản cũ** đọc văn bản thô qua `chunk_law` và `fixed_chunk` (có `articles`, kiểm tra overlap); `chunk_id` dạng `BLDS2015_Dieu357_Khoan1`. Task 1 của plan Sprint 2 sẽ chuyển sang đọc JSON cấu trúc.
- `src/ingestion/index.py`: nạp ChromaDB; metadata có `effective_from`/`effective_to` dạng `YYYYMMDD`.
- `src/generation/llm.py`: client OpenAI-compatible, cache `.cache/llm`, `chat_json`, `from_env("LLM"|"JUDGE")`.
- `tests/`: test_legal_chunker, test_index, test_llm.

Dữ liệu (do Hùng, đã push): `data/raw/*.doc` → `data/normalized/*.md` (MinerU) → `data/structured/*.json` (`data/legal_structure_parser.py`) → chunk riêng của Hùng ở `data/chunks/` và `data/legal_chunker.py` (**không dùng**, chuẩn là bộ chunker trong `src/ingestion`). Số Điều đã khớp: BLDS 689, BLLĐ 220, LDN 218, LTM 324. `data/test_cases.json` = 65 câu synthetic (65, không phải 58). `data/raw/laws.json` = metadata 4 luật (do Claude điền, **chưa đối chiếu nguồn**, chưa có BLLĐ 2012 và chưa có trường `domain`).

**Chưa làm:** chạy chunker/index trên dữ liệu thật; gọi thử API Gemini/Groq (chưa có `.env`); toàn bộ `src/retrieval`, `src/agent`, `src/api`, `eval/`.

Zalo: bản clone `zalo-ai-legal-text-retrieval-vn/` (đã `git lfs pull`, bị `.gitignore`). Plan Sprint 2 Task 2 Step 5 copy `queries.jsonl` và `qrels/{train,test}.jsonl` từ đó sang `data/external/zalo/`. Đo được: 3196 câu, **81 câu** có mọi căn cứ trong 4 luật (64 BLDS + 21 LDN), 0 câu BLLĐ/LTM.

## 5. Việc tiếp theo

1. Người dùng push các commit hiện tại để Hùng `git pull` và bắt đầu thẻ H1–H7.
2. **Thực thi plan Đạt Sprint 2** theo cách **Native** (Claude tự làm cả 8 task trong một phiên rồi một reviewer Opus kiểm tra toàn bộ; không commit, người dùng tự commit): dùng skill `superpowers:executing-plans` với `docs/superpowers/plans/2026-10-15-sprint2-dat.md`. Người dùng chưa chọn xong giữa Native và Subagent-driven; Claude khuyên Native.
3. Task 1 chạy trên dữ liệu thật ngay đầu: nếu số Điều lệch thì debug ở `render_text`.
4. Sau Sprint 2 (hạn 21/10): viết plan Sprint 3 (tác tử, đầu sprint, dựa trên interface và số liệu thật của Sprint 2). **Viết plan từng sprint, không viết một lần**, cho cả Đạt (TDD) và Hùng (thẻ việc).
5. Việc người dùng tự làm: lấy key Gemini (aistudio.google.com) và Groq (console.groq.com), `cp .env.example .env`; gửi email tóm tắt thay đổi đề cương cho thầy Lê Anh Cường.

## 6. Rủi ro và lưu ý

- **Tài liệu tham khảo** (mục 12 của đề cương): đã xác minh bài Pham et al. (KMIS 2025), Reuter et al. (NLLP 2025), VLQA (arXiv 2507.19995), Nguyen Ba et al. (arXiv 2409.13699). **Chưa tra lại**: số trang của RAGAS, ALCE, RRF; danh sách tác giả BGE-M3; URL `challenge.zalo.ai`.
- Số hiệu, ngày ban hành/hiệu lực của BLLĐ 2012 (10/2012/QH13, 2013-05-01, hết hiệu lực 2021-01-01) và các ví dụ (câu Q001, Điều 22) trong Phụ lục A là **trí nhớ của Claude, chưa kiểm**; Hùng kiểm ở H2.
- Câu synthetic có thể dễ hơn câu thật (câu hỏi bám sát câu chữ điều luật, làm Hit@5 cao ảo): đây là giả thuyết, RQ1 sẽ đo; báo cáo luôn tách theo nguồn.
- Các lỗi nhỏ còn hoãn ở `llm.py` (xem `.superpowers/sdd/2026-10-09-sprint1-core/progress.md` nếu còn): regex JSON tham lam, `chat_json` cache output hỏng, trùng file `.tmp` khi gọi song song, khóa cache thiếu `base_url`, `.env` tìm theo thư mục chạy lệnh. Xử lý trước Sprint 3–4.
- Plan Đạt chưa được chạy thử: số test dự kiến trong plan là đếm tay, có thể lệch.
- File `.superpowers/` bị `.gitignore`; không phụ thuộc vào nó.
