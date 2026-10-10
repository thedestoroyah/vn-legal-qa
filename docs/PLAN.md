# Kế hoạch thực hiện

Hạn nộp **23:59 21/11/2026**. Thiết kế: [specs/2026-10-09-agentic-legal-qa-design.md](superpowers/specs/2026-10-09-agentic-legal-qa-design.md). Định dạng dữ liệu chung (file raw, laws.json, chunk, test case, API): Phụ lục A trong đề cương. Bản này đồng bộ với Phụ lục B của đề cương; sửa một bên thì sửa cả bên kia.

Đánh dấu `[x]` khi xong. *Xong khi* = tiêu chí nghiệm thu.

## Sprint 1 (09/10 – 14/10/2026): Dữ liệu và nền tảng

**Mục tiêu sprint:** kho dữ liệu 5 văn bản đã phân đoạn và nạp ChromaDB; client LLM sẵn sàng; 30 câu kiểm thử đầu tiên.

### Phạm Huỳnh Quốc Đạt

- [x] Khởi tạo repository, cấu trúc thư mục, requirements.txt (cố định phiên bản), README hướng dẫn cài đặt.
- [x] legal_chunker.py: tách Chương → Mục → Điều → Khoản, giữ Điểm trong Khoản; hàm fixed_chunk cho baseline RQ2; kiểm thử tự động.
- [x] index.py: nạp chunk vào ChromaDB kèm metadata, văn bản embed có gắn tiêu đề phân cấp; cờ --rebuild, --query; kiểm thử tự động.
- [x] Bổ sung trường expiry_date từ laws.json vào từng chunk. *Xong khi:* kiểm thử chunk của BLLD2012 có expiry_date = "2021-01-01".
- [x] fixed_chunk ghi danh sách các Điều mà mỗi đoạn cố định phủ qua (trường "articles") để đánh giá RQ2 ở cấp Điều. *Xong khi:* kiểm thử một đoạn nằm vắt qua hai Điều trả về đủ cả hai.
- [ ] Chạy chunker trên 5 file của Hùng; đối chiếu số Điều với mục lục văn bản (BLDS2015: 689, BLLD2019: 220, BLLD2012: 242, LDN2020: 218, LTM2005: 324, cộng các điều bổ sung trong bản hợp nhất). *Xong khi:* số Điều khớp, không có chunk rỗng.
- [ ] Sửa bộ tách cho các trường hợp phát sinh từ dữ liệu thật (điều bị bãi bỏ, điều có số kèm chữ như 50a, dòng chú thích sửa đổi còn sót).
- [ ] Chạy index.py với BGE-M3 trên dữ liệu thật. *Xong khi:* truy vấn "lãi chậm trả tiền" trả về BLDS2015 Điều 357 trong top-5.
- [x] src/generation/llm.py: client tương thích OpenAI (LLM_BASE_URL, LLM_API_KEY, LLM_MODEL đọc từ .env); cache xuống đĩa theo hash (model, messages, tham số); tự chờ và thử lại khi gặp lỗi 429; đếm số lượt gọi; hàm chat_json phân tích JSON, thử lại 1 lần khi lỗi. *Xong khi:* kiểm thử với client giả chứng minh lần gọi thứ hai lấy từ cache và lỗi 429 được thử lại.
- [ ] Cập nhật .env.example (LLM_*, JUDGE_*, EMBED_MODEL); đăng ký API key Gemini và Groq, gọi thử mỗi bên 1 lần.

### Hoàng Sinh Hùng

- [ ] Tải toàn văn 5 văn bản từ vbpl.vn hoặc thuvienphapluat.vn: 4 luật ở dạng văn bản hợp nhất mới nhất và Bộ luật Lao động 2012 bản gốc. Lưu file gốc vào data/raw/source/ để truy vết.
- [ ] Chuyển 5 văn bản sang định dạng Phụ lục A.1 (data/raw/<LAW_ID>.md). *Xong khi:* đúng quy ước dòng, không còn số trang, chú thích [n], phần ký tên.
- [ ] Kiểm tra chất lượng: đối chiếu ngẫu nhiên 10 Điều mỗi văn bản với bản gốc (nội dung, số khoản, số điểm); ghi kết quả vào docs/data_check.md.
- [ ] Hoàn thiện data/raw/laws.json theo Phụ lục A.2 cho cả 5 văn bản (thêm BLLD2012, thêm expiry_date, ghi số hiệu văn bản hợp nhất và nguồn). *Xong khi:* số hiệu và các ngày đã đối chiếu với nguồn chính thức.
- [ ] Xin quyền truy cập bộ VLQA (email nhóm tác giả hoặc đăng ký nhiệm vụ DRiLL VLSP 2025). Hạn 12/10; nếu không được thì tải bộ Zalo AI Legal Text Retrieval 2021.
- [ ] Viết eval/README.md: quy ước gán nhãn theo Phụ lục A.4 (gán ở cấp Khoản, liệt kê đủ căn cứ, cách ghi event_date).
- [ ] Soạn 30 câu đầu tiên trong eval/test_cases.json, ưu tiên 10 câu temporal trước (điểm khác biệt giữa BLLD2012 và BLLD2019: hợp đồng lao động theo mùa vụ, quyền đơn phương chấm dứt hợp đồng của người lao động, thời hạn báo trước, tuổi nghỉ hưu, giới hạn giờ làm thêm), còn lại là câu situational.

**Cả hai:** thống nhất Phụ lục A ngày 10/10; họp nhanh 10 phút mỗi tối.

**Nghiệm thu sprint (14/10):** chunks.jsonl đủ 5 văn bản; ChromaDB đã nạp; 30 câu kiểm thử đúng schema.

## Sprint 2 (15/10 – 21/10/2026): Truy xuất và thực nghiệm RQ1, RQ2

**Mục tiêu sprint:** hàm search hoàn chỉnh có lọc hiệu lực; có bảng số liệu RQ1, RQ2; đủ 80 câu kiểm thử.

### Phạm Huỳnh Quốc Đạt

- [ ] src/retrieval/bm25.py: tách từ bằng underthesea, chuyển chữ thường, bỏ dấu câu; BM25Okapi (rank-bm25); lưu chỉ mục ra đĩa. *Xong khi:* kiểm thử truy vấn chứa đúng thuật ngữ trả về đúng chunk.
- [ ] src/retrieval/dense.py: truy vấn ChromaDB có điều kiện lọc theo khoảng hiệu lực.
- [ ] src/retrieval/hybrid.py: hợp nhất BM25 và Dense bằng RRF (k = 60); xếp hạng lại top-20 bằng bge-reranker-v2-m3.
- [ ] Hàm search(query, k=5, date=None, mode="hybrid_rerank"), mode ∈ {bm25, dense, hybrid, hybrid_rerank}. date = None thì chỉ giữ văn bản còn hiệu lực; có date thì lọc effective_date ≤ date < expiry_date, áp dụng cho cả BM25. *Xong khi:* kiểm thử với date năm 2020 không trả về chunk BLLD2019 và ngược lại.
- [ ] Hàm get_article(law_id, article): trả về toàn văn một Điều (nối các Khoản theo thứ tự).
- [ ] Bốn biến thể phân đoạn cho RQ2, mỗi biến thể một collection: fixed-size; theo Khoản không gắn tiêu đề; theo Khoản có gắn tiêu đề phân cấp; theo Khoản có gắn tiêu đề và mở rộng ngữ cảnh lên Điều cha khi trả kết quả.
- [ ] eval/evaluate.py (phần truy xuất): chạy mọi cấu hình RQ1 và RQ2 trên tập kiểm thử; tính Hit@5, Recall@10, MRR@10 ở cấp Khoản và cấp Điều, DRM@5; ghi eval/results/retrieval_<cấu hình>.csv và bảng tổng hợp dạng markdown.
- [ ] Kiểm thử cho các hàm tính chỉ số (ví dụ nhỏ tính tay).
- [ ] Đo thời gian rerank trên CPU; nếu vượt 3 giây/câu thì giảm từ top-20 xuống top-10 và ghi lại lựa chọn.
- [ ] Kiểm chéo căn cứ cho 40 câu kiểm thử do Hùng soạn.

### Hoàng Sinh Hùng

- [ ] Hoàn thành 80 câu kiểm thử: khoảng 60 situational (khoảng 15 câu mỗi lĩnh vực: dân sự, lao động, doanh nghiệp, thương mại), 10–15 temporal, 5 direct ("Điều X Luật Y quy định gì"), 5 out_of_scope (hình sự, giao thông, đất đai, thuế, hành chính).
- [ ] Chọn lọc câu hỏi từ VLQA (hoặc Zalo): giữ câu có điều luật liên quan thuộc 5 văn bản, gán lại gold_citations theo chunk_id của kho, viết reference_answer ngắn gọn, ghi source.
- [ ] eval/validate_cases.py: kiểm tra mọi câu đúng schema, mọi gold chunk_id tồn tại trong chunks.jsonl, phân bổ số câu theo loại và lĩnh vực đúng kế hoạch. *Xong khi:* script chạy không lỗi trên 80 câu.
- [ ] Kiểm chéo căn cứ cho các câu do Đạt soạn hoặc chọn lọc (nếu có).
- [ ] Phác thảo wireframe giao diện (giấy hoặc Figma): khung chat bên trái, panel nguyên văn điều luật bên phải, khu vực vết thực thi của tác tử.
- [ ] Khung Streamlit src/ui/app.py: bố cục 2 cột, hiển thị một phản hồi mẫu (file JSON giả đúng định dạng Phụ lục A.5).

**Nghiệm thu sprint (21/10):** bảng RQ1 và RQ2 có số liệu thật; validate_cases.py chạy sạch trên 80 câu.

## Sprint 3 (22/10 – 28/10/2026): Tác tử Agentic-RAG

**Mục tiêu sprint:** tác tử chạy được qua dòng lệnh với đủ các nhánh; giao diện chạy với dữ liệu mẫu.

### Phạm Huỳnh Quốc Đạt

- [ ] src/agent/state.py: trạng thái tác tử (question, route_type, event_date, direct_ref, queries, evidence, n_rewrites, answer, citations, refused, trace).
- [ ] src/generation/prompts.py: prompt tiếng Việt cho route, grade, generate, verify; đầu ra JSON; mỗi prompt có 2 ví dụ mẫu.
- [ ] Nút route: phân loại situational / direct / out_of_scope; trích event_date (ISO hoặc null); với câu direct trích law_id và số Điều.
- [ ] Nút lookup_article: gọi get_article cho câu direct.
- [ ] Nút retrieve: gọi search với date = event_date; không lọc theo lĩnh vực.
- [ ] Nút grade: đánh giá top-5 có đủ để trả lời không; nếu không thì đề xuất truy vấn mới; tối đa 2 vòng, hết vòng vẫn thiếu thì trả lời "không đủ căn cứ".
- [ ] Nút generate: sinh câu trả lời, mỗi khẳng định gắn [chunk_id].
- [ ] Nút verify: (a) tách mã trích dẫn bằng biểu thức chính quy, loại mã không có trong ngữ cảnh; (b) gửi một lượt LLM kiểm tra từng cặp (câu, đoạn được trích), gỡ trích dẫn không được hỗ trợ; câu mất hết căn cứ thì sinh lại 1 lần, sau đó vẫn còn thì gắn nhãn "chưa có căn cứ".
- [ ] src/agent/graph.py: StateGraph LangGraph nối các nút bằng cạnh có điều kiện; cấu hình baseline / full / no_router / no_grading / no_verify; ghi trace (tên nút, đầu ra tóm tắt, thời gian, số lượt gọi LLM).
- [ ] CLI: python -m src.agent.run "câu hỏi" --config full, in câu trả lời và trace.
- [ ] Kiểm thử với LLM giả: từng nút; đồ thị đi đúng nhánh out_of_scope, direct, vòng viết lại dừng sau 2 lần, verify gỡ trích dẫn sai.
- [ ] Chạy thử 10 câu thật với Gemini/Groq, ghi lại các lỗi prompt để chỉnh.

### Hoàng Sinh Hùng

- [ ] Giao diện chat (st.chat_message): hiển thị câu trả lời, thẻ trích dẫn dạng nút bấm.
- [ ] Bấm thẻ trích dẫn: panel bên phải hiện toàn văn Điều, làm nổi bật Khoản được trích.
- [ ] Khu vực "Các bước tác tử" (st.expander) hiển thị trace: định tuyến, truy vấn đã viết lại, trích dẫn bị loại khi kiểm chứng.
- [ ] Hiển thị trạng thái từ chối và nhãn "chưa có căn cứ"; dòng lưu ý "thông tin tham khảo, không thay thế tư vấn pháp lý".
- [ ] Soạn bản nháp prompt chấm (judge) cho Faithfulness và Answer Correctness theo định nghĩa RAGAS (Đạt duyệt lại).
- [ ] Soạn thang chấm tay 3 mức (0 / 0,5 / 1) cho 2 tiêu chí trên, kèm ví dụ.
- [ ] Bắt đầu Chương 2 báo cáo (cơ sở lý thuyết: BM25, dense retrieval, RRF, cross-encoder, RAG, Agentic-RAG, LangGraph).

**Nghiệm thu sprint (28/10):** CLI trả lời đúng nhánh cho 4 loại câu hỏi; giao diện chạy với dữ liệu mẫu. Nếu tác tử chưa ổn định: áp dụng phương án dự phòng tại mục 11.

## Sprint 4 (29/10 – 04/11/2026): Tích hợp hệ thống và đánh giá câu trả lời

**Mục tiêu sprint:** bản thử nghiệm chạy từ đầu đến cuối; pipeline đánh giá câu trả lời chạy được.

### Phạm Huỳnh Quốc Đạt

- [ ] src/api/main.py (FastAPI): POST /api/ask theo Phụ lục A.5; GET /api/article/{law_id}/{article}; GET /health. Nạp mô hình một lần khi khởi động.
- [ ] Kiểm tra đầu vào (câu hỏi rỗng, dài quá 1000 ký tự, config không hợp lệ trả 422); lỗi LLM trả 503 với thông báo thân thiện, ghi log chi tiết phía server.
- [ ] eval/evaluate.py (phần sinh): chạy 5 cấu hình cho 80 câu; tính Citation Precision/Recall ở cấp Điều, tỷ lệ từ chối đúng, tỷ lệ đúng phiên bản (câu temporal), độ trễ, số lượt gọi LLM; lưu toàn bộ đầu ra thô ra JSONL để chấm lại không cần chạy lại tác tử.
- [ ] Bộ chấm LLM-as-a-judge chạy trên nhà cung cấp khác với tác tử (JUDGE_*), một lượt gọi mỗi câu trả lời.
- [ ] Chạy thử toàn bộ pipeline trên 10 câu; đo quota thực tế và ước lượng thời gian chạy đủ.
- [ ] Chấm tay độc lập 20 câu trả lời (cùng Hùng).

### Hoàng Sinh Hùng

- [ ] Ghép giao diện với API: gọi /api/ask và /api/article, hiển thị trạng thái đang xử lý, xử lý lỗi API.
- [ ] Kiểm thử trải nghiệm với 10 câu hỏi; ghi lỗi vào GitHub Issues.
- [ ] Chấm tay độc lập 20 câu trả lời; tính mức đồng thuận giữa người chấm và bộ chấm LLM (tỷ lệ khớp).
- [ ] Viết Chương 1 (tổng quan đề tài) và tiếp tục Chương 2.

**Nghiệm thu sprint (04/11):** hỏi trên giao diện nhận câu trả lời thật kèm trích dẫn bấm được; evaluate.py chạy được trên 10 câu.

## Sprint 5 (05/11 – 11/11/2026): Thực nghiệm đầy đủ và viết báo cáo

**Mục tiêu sprint:** đủ số liệu cho RQ1–RQ4; bản nháp báo cáo khoảng 80%. Đóng băng tính năng ngày 08/11 (sau ngày này chỉ sửa lỗi).

### Phạm Huỳnh Quốc Đạt

- [ ] Chạy đủ RQ3 (5 cấu hình × 80 câu) và RQ4 (3 chế độ lọc × 10–15 câu temporal), rải trong 2–3 ngày theo quota.
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
