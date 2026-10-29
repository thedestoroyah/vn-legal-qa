# Kế hoạch thực hiện

Hạn nộp **23:59 21/11/2026**. Thiết kế: [specs/2026-10-09-agentic-legal-qa-design.md](superpowers/specs/2026-10-09-agentic-legal-qa-design.md). Định dạng dữ liệu chung (file raw, laws.json, chunk, test case, API): Phụ lục A trong [đề cương](managements/Đề%20cương%20DACNTT.md). Bản này đồng bộ với Phụ lục B của [đề cương](managements/Đề%20cương%20DACNTT.md); sửa một bên thì sửa cả bên kia.

Đánh dấu `[x]` khi xong. *Xong khi* = tiêu chí nghiệm thu.

## Sprint 1 (09/10 – 14/10/2026): Dữ liệu và nền tảng

**Mục tiêu sprint:** kho dữ liệu 5 văn bản đã phân đoạn và nạp ChromaDB; client LLM sẵn sàng; 30 câu kiểm thử đầu tiên.

### Phạm Huỳnh Quốc Đạt

- [x] Khởi tạo repository, cấu trúc thư mục, requirements.txt (cố định phiên bản), README hướng dẫn cài đặt.
- [x] legal_chunker.py: tách Chương → Mục → Điều → Khoản, giữ Điểm trong Khoản; hàm fixed_chunk cho baseline RQ2; kiểm thử tự động.
- [x] index.py: nạp chunk vào ChromaDB kèm metadata, văn bản embed có gắn tiêu đề phân cấp; cờ --rebuild, --query; kiểm thử tự động.
- [x] Bổ sung trường expiry_date từ laws.json vào từng chunk. *Xong khi:* kiểm thử chunk của BLLD2012 có expiry_date = "2021-01-01".
- [x] fixed_chunk ghi danh sách các Điều mà mỗi đoạn cố định phủ qua (trường "articles") để đánh giá RQ2 ở cấp Điều. *Xong khi:* kiểm thử một đoạn nằm vắt qua hai Điều trả về đủ cả hai.
- [x] Chạy chunker trên 5 file của Hùng; đối chiếu số Điều với mục lục văn bản (BLDS2015: 689, BLLD2019: 220, BLLD2012: 242, LDN2020: 218, LTM2005: 324, cộng các điều bổ sung trong bản hợp nhất). *Xong khi:* số Điều khớp, không có chunk rỗng. → *chuyển sang Sprint 2 (Task 1, 8).*
- [x] Sửa bộ tách cho các trường hợp phát sinh từ dữ liệu thật (điều bị bãi bỏ, điều có số kèm chữ như 50a, dòng chú thích sửa đổi còn sót). → *chuyển sang Sprint 2 (Task 1, 8).*
- [x] Chạy index.py với BGE-M3 trên dữ liệu thật. *Xong khi:* truy vấn "lãi chậm trả tiền" trả về BLDS2015 Điều 357 trong top-5. → *chuyển sang Sprint 2 (Task 1, 8).*
- [x] src/generation/llm.py: client tương thích OpenAI (LLM_BASE_URL, LLM_API_KEY, LLM_MODEL đọc từ .env); cache xuống đĩa theo hash (model, messages, tham số); tự chờ và thử lại khi gặp lỗi 429; đếm số lượt gọi; hàm chat_json phân tích JSON, thử lại 1 lần khi lỗi. *Xong khi:* kiểm thử với client giả chứng minh lần gọi thứ hai lấy từ cache và lỗi 429 được thử lại.
- [x] Cập nhật .env.example (LLM_*, JUDGE_*, EMBED_MODEL); đăng ký API key Gemini và Groq, gọi thử mỗi bên 1 lần. → Gemini (gemini-3.1-flash-lite) gọi thử xong 16/10; Groq chuyển sang Sprint 4.

### Hoàng Sinh Hùng

- [x] Tải và chuẩn hóa 4 luật (BLDS 2015, BLLĐ 2019, LDN 2020, LTM 2005) bằng pipeline .doc → MinerU → normalized/*.md → structured/*.json; số Điều khớp mục lục. (Văn bản gốc, chưa hợp nhất sửa đổi — ghi là giới hạn.)
- [x] Định dạng Phụ lục A.1 cũ (data/raw/<LAW_ID>.md) được thay bằng JSON cấu trúc (Phụ lục A.1 cập nhật 15/10).
- [x] Soạn 65 câu kiểm thử đầu tiên (data/test_cases.json, sinh bằng AI → nguồn synthetic).
- [x] BLLĐ 2012, laws.json, kiểm tra chất lượng → chuyển sang Sprint 2 (H1–H3).
- [ ] ~~Xin VLQA: hủy — dữ liệu chưa được công bố (kiểm tra 15/10); thay bằng Zalo AI 2021.~~
- [ ] ~~eval/README.md: hủy — quy ước gán nhãn nằm trong thẻ H6 của plan Sprint 2.~~

**Cả hai:** thống nhất Phụ lục A ngày 10/10; họp nhanh 10 phút mỗi tối.

**Nghiệm thu sprint (14/10):** chunks.jsonl đủ 5 văn bản; ChromaDB đã nạp; 30 câu kiểm thử đúng schema.

## Sprint 2 (15/10 – 21/10/2026): Truy xuất và thực nghiệm RQ1, RQ2

**Mục tiêu sprint:** kho chunk đọc từ JSON cấu trúc; truy xuất BM25 / Dense / Hybrid / Hybrid + rerank có lọc hiệu lực; tập kiểm thử 3 nguồn (zalo, synthetic, manual) hợp lệ; bảng số liệu RQ1, RQ2.

### Phạm Huỳnh Quốc Đạt — chi tiết: [docs/superpowers/plans/2026-10-15-sprint2-dat.md](superpowers/plans/2026-10-15-sprint2-dat.md)

- [x] Task 1 — Bộ phân đoạn đọc data/structured/*.json, sinh chunks.jsonl (Khoản), chunks_article.jsonl (Điều), chunks_fixed.jsonl. Xong khi: BLDS 689, BLLĐ 220, LDN 218, LTM 324 Điều (BLLĐ 2012: 242 khi Hùng xong H1).
- [x] Task 2 — eval/cases.py (kiểm tra hợp lệ), eval/import_cases.py (gộp zalo + synthetic + manual), eval/show_article.py; tải tập con Zalo vào data/external/zalo/; thêm domain vào laws.json. Xong khi: python -m eval.import_cases ghi eval/test_cases.json không lỗi.
- [x] Task 3 — Chỉ mục theo 4 biến thể RQ2 (--variant clause_header / clause_plain / article / fixed).
- [x] Task 4 — Lọc hiệu lực theo ngày (filters.py) và BM25 (underthesea).
- [x] Task 5 — Dense trên Chroma có lọc hiệu lực.
- [x] Task 6 — Retriever: RRF (k=60), rerank bge-reranker-v2-m3 top-20, get_article, load_retriever.
- [x] Task 7 — eval/metrics.py + eval/evaluate.py --rq rq1|rq2: Hit@5, Recall@10, MRR@10 (Điều, Khoản), DRM@5, tách theo nguồn.
- [x] Task 8 — Chạy thật (bỏ qua gọi thử API LLM: chưa có key): nạp 4 chỉ mục, đo rerank (> 3 s/câu thì top-10), chạy RQ1 và RQ2, gọi thử API LLM (việc Sprint 1). Xong khi: có eval/results/retrieval_rq1.md và retrieval_rq2.md.
- [x] Kiểm chéo căn cứ các câu manual của Hùng (đổi checked_by thành "Dat").

### Hoàng Sinh Hùng — chi tiết: [docs/sprints/2026-10-15-sprint2-hung.md](sprints/2026-10-15-sprint2-hung.md)

- [x] H1 — Thêm BLLĐ 2012 (structured JSON, 242 Điều).
- [x] H2 — Hoàn thiện laws.json: đối chiếu 4 luật với nguồn chính thức, thêm BLLD2012, domain, source.
- [x] H3 — docs/data_check.md: đối chiếu 10 Điều ngẫu nhiên mỗi văn bản với bản gốc.
- [x] H4 — Duyệt khoảng 81 câu Zalo, câu loại ghi vào eval/zalo_exclude.txt.
- [x] H5 — docs/synthetic_check.md: kiểm định 20/65 câu synthetic, sửa câu sai.
- [x] H6 — eval/manual_cases.json: ~15 situational (BLLĐ, LTM), 10–15 temporal, ~5 direct, ~5 out_of_scope.
- [x] H7 — Khung Streamlit src/ui/app.py với phản hồi mẫu (Phụ lục A.5).

**Nghiệm thu sprint (21/10):** bảng RQ1 và RQ2 có số liệu thật; python -m eval.import_cases chạy không lỗi với đủ 3 nguồn; giao diện mẫu chạy được.

## Sprint 3 (22/10 – 28/10/2026): Tác tử Agentic-RAG

**Mục tiêu sprint:** tác tử chạy được qua dòng lệnh với đủ các nhánh; giao diện chạy với dữ liệu mẫu.

### Phạm Huỳnh Quốc Đạt — chi tiết: [docs/superpowers/plans/2026-10-16-sprint3-dat.md](superpowers/plans/2026-10-16-sprint3-dat.md)

- [x] Task 1 — langgraph 1.2.15; gia cố llm.py: đếm lượt gọi logic (requests), giãn cách LLM_MIN_INTERVAL theo 15 RPM, parse JSON không tham lam, xóa cache JSON hỏng, .env theo gốc repo.
- [x] Task 2 — src/generation/citations.py: tách/gỡ/gắn nhãn [chunk_id] theo câu (verify a, b).
- [x] Task 3 — src/generation/prompts.py: 4 prompt tiếng Việt (route, grade, generate, verify), mỗi prompt ≥ 2 ví dụ, đầu ra JSON.
- [x] Task 4 — src/agent/state.py (trạng thái, 5 cấu hình) và nút route (chuẩn hóa law_id, event_date), lookup_article, retrieve (date = event_date, không lọc lĩnh vực), refuse.
- [x] Task 5 — Nút grade (≤ 2 vòng viết lại), generate (gắn [chunk_id], KHÔNG_ĐỦ_CĂN_CỨ), verify (a) regex + (b) một lượt LLM theo cặp (câu, đoạn); câu mất hết căn cứ sinh lại 1 lần rồi gắn nhãn "chưa có căn cứ".
- [x] Task 6 — src/agent/graph.py: StateGraph, cạnh có điều kiện, baseline / full / no_router / no_grading / no_verify, trace {node, output, ms, llm_calls}. Xong khi: test đi đúng nhánh out_of_scope, direct, vòng viết lại dừng sau 2 lần, verify gỡ trích dẫn sai.
- [x] Task 7 — src/agent/run.py: Agent.run(question, config) theo Phụ lục A.5; CLI python -m src.agent.run "câu hỏi" --config full.
- [x] Task 8 — eval/agent_smoke.py: chạy thử 10 câu thật với Gemini, ghi lỗi prompt vào eval/results/agent_smoke.md, chỉnh prompt tối đa 2 vòng.

### Hoàng Sinh Hùng — chi tiết: [docs/sprints/2026-10-16-sprint3-hung.md](sprints/2026-10-16-sprint3-hung.md)

- [x] Làm trước các thẻ Sprint 2 còn dở (ưu tiên H1, H2, H6).
- [x] H8 — Panel toàn văn Điều, tô sáng Khoản được trích (src/ui/article_view.py, sample_articles.json).
- [ ] H9 — Hiển thị từ chối, nhãn "(chưa có căn cứ)", dòng tóm tắt từng bước trace; 3 phản hồi mẫu trong src/ui/samples/.
- [ ] ~~H10 — docs/judge_prompts.md~~ → thay bằng H10' (Sprint 4): duyệt prompt chấm trong eval/judge.py.: prompt chấm Faithfulness và Answer Correctness (0 / 0,5 / 1, đầu ra JSON) theo RAGAS (Đạt duyệt).
- [ ] H11 — docs/rubric.md: thang chấm tay 3 mức kèm ví dụ và quy tắc biên.
- [ ] H12 — Bản nháp Chương 2 (BM25, dense, RRF, cross-encoder, RAG, Agentic-RAG, LangGraph, đặc thù văn bản luật).

**Nghiệm thu sprint (28/10):** CLI trả lời đúng nhánh cho 4 loại câu hỏi; giao diện chạy với dữ liệu mẫu. Nếu tác tử chưa ổn định: áp dụng phương án dự phòng tại mục 11.

## Sprint 4 (29/10 – 04/11/2026): Tích hợp hệ thống và đánh giá câu trả lời

**Mục tiêu sprint:** bản thử nghiệm chạy từ đầu đến cuối; pipeline đánh giá câu trả lời chạy được.

### Phạm Huỳnh Quốc Đạt — chi tiết: [docs/superpowers/plans/2026-10-28-sprint4-dat.md](superpowers/plans/2026-10-28-sprint4-dat.md)

- [x] Task 1 — RQ4: chính sách lọc hiệu lực event / current / any (filters.ANY_DATE, date_policy trong state, Agent.run(question, config, date_policy)); route chịu được type không phải chuỗi.
- [x] Task 2 — eval/metrics.py: Citation P/R cấp Điều, tỷ lệ từ chối đúng, tỷ lệ đúng phiên bản (câu temporal).
- [x] Task 3 — eval/agent_eval.py run/report: chạy RQ3 (5 cấu hình; ablation trên mẫu phân tầng 60 câu) và RQ4 (12 câu temporal × 3 chính sách); ghi nối JSONL, chạy tiếp được, dừng êm khi hết quota.
- [x] Task 4 — eval/judge.py (Groq gpt-oss-120b, 1 lượt/câu, Faithfulness + Correctness 0 / 0,5 / 1; từ chối và câu ngoài phạm vi chấm bằng code); agent_eval judge/sheet/agree (phiếu chấm tay CSV, tỷ lệ khớp).
- [x] Task 5 — src/api/main.py: POST /api/ask (422 đầu vào sai, 503 LLM lỗi, phục vụ tuần tự), GET /api/article/{law_id}/{article}, GET /health; nạp mô hình một lần khi khởi động.
- [x] Task 6 — Chạy thử pipeline trên 10 câu RQ3 + 12 câu RQ4, đo quota thực tế, ghi lịch chạy đủ vào Sprint 5.
- [ ] Chấm tay độc lập 20 câu trả lời (cùng Hùng, phiếu eval/results/grading_rq3.csv).

### Hoàng Sinh Hùng — chi tiết: [docs/sprints/2026-10-28-sprint4-hung.md](sprints/2026-10-28-sprint4-hung.md)

- [ ] Làm nốt thẻ Sprint 3: H9, H10' (duyệt prompt chấm trong eval/judge.py thay cho H10), H11, H12.
- [ ] H16 — Xem lại câu M_017 (đáp án mẫu dễ tranh cãi).
- [ ] H13 — Ghép giao diện với API (API_URL; không đặt thì dùng phản hồi mẫu), vòng chờ, thông báo lỗi; kiểm cùng Đạt.
- [ ] H14 — Chấm tay độc lập 20 câu; tỷ lệ khớp người–LLM và giữa 2 người ghi vào docs/rubric.md.
- [ ] H15 — Bản nháp Chương 1 (tổng quan đề tài).

**Nghiệm thu sprint (04/11):** hỏi trên giao diện nhận câu trả lời thật kèm trích dẫn bấm được; evaluate.py chạy được trên 10 câu.

## Sprint 5 (05/11 – 11/11/2026): Thực nghiệm đầy đủ và viết báo cáo

**Mục tiêu sprint:** đủ số liệu cho RQ1–RQ4; bản nháp báo cáo khoảng 80%. Đóng băng tính năng ngày 08/11 (sau ngày này chỉ sửa lỗi).

### Phạm Huỳnh Quốc Đạt

- [ ] Chạy đủ RQ3 theo lịch (đo 28/10: full ≈ 3,6 lượt Gemini thật/câu; baseline và ablation gần như trúng cache): ngày 1 `run --rq rq3 --configs full` (115 câu còn lại, ≈ 410 lượt); ngày 2 `--configs baseline` (179 câu) và `--configs no_router no_grading no_verify --subset 60` (≈ 150 lượt); mỗi ngày ≤ 450 lượt, judge (Groq) sau mỗi ngày. RQ4 đã chạy đủ 28/10 (12 câu temporal × 3 chính sách); chạy lại nếu Hùng sửa câu temporal (H16). Chạy lại RQ1/RQ2 (`eval.evaluate`) vì Zalo còn 77 câu.
- [ ] Chạy riêng 20 câu không dùng cache để đo độ trễ.
- [ ] Bảng tổng hợp và biểu đồ (matplotlib) cho từng RQ.
- [ ] Phân tích lỗi trên 20 trường hợp sai, phân loại: truy xuất sai Điều, sai văn bản (DRM), sai phiên bản, trích dẫn không được hỗ trợ, định tuyến sai.
- [ ] Viết Chương 3 (thiết kế hệ thống, kiến trúc) và Chương 4 (thực nghiệm và kết quả).

### Hoàng Sinh Hùng

- [ ] Hỗ trợ phân tích lỗi: đọc đầu ra, gán loại lỗi.
- [ ] Hoàn thành Chương 1 và Chương 2.
- [ ] Sơ đồ: use case, activity (luồng hỏi đáp), sequence (UI → API → tác tử), kiến trúc tổng thể; ảnh chụp giao diện.
- [ ] Bản nháp Chương 5 (kết luận, hạn chế, hướng phát triển).

**Nghiệm thu sprint (11/11):** đủ bảng số liệu và biểu đồ RQ1–RQ4; bản nháp báo cáo khoảng 80%.

## Sprint 6 (12/11 – 21/11/2026): Đóng gói và hoàn thiện

### Phạm Huỳnh Quốc Đạt

- [ ] Dockerfile và docker-compose (dịch vụ api và ui, volume cho chroma_db và cache mô hình).
- [ ] README: cài đặt, chạy ứng dụng, tái lập thực nghiệm (lệnh evaluate.py cho từng RQ).
- [ ] Dọn mã nguồn: xóa file thừa, chạy linter, toàn bộ kiểm thử đạt.
- [ ] Rà soát kỹ thuật toàn bộ báo cáo; kiểm tra Turnitin.

### Hoàng Sinh Hùng

- [ ] Định dạng báo cáo theo mẫu TDTU (mục lục, danh mục hình và bảng, tài liệu tham khảo APA).
- [ ] Slide bảo vệ (15–20 slide): vấn đề → câu hỏi nghiên cứu → kiến trúc → demo → kết quả RQ1–RQ4 → hạn chế và hướng phát triển.
- [ ] Video demo 3–5 phút với 4 kịch bản: câu tình huống, câu có mốc thời gian năm 2020, câu ngoài phạm vi bị từ chối, câu tra cứu trực tiếp điều luật.

### Cả hai

- [ ] 18/11: báo cáo hoàn chỉnh. 19–20/11: dự phòng và tập dượt bảo vệ. 21/11: nộp trước 23:59.
