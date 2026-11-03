# CHƯƠNG 3. THIẾT KẾ VÀ XÂY DỰNG HỆ THỐNG

> **Bản nháp Task 6 Sprint 5** — Đạt, 03/11/2026. Viết Markdown để chép vào file báo cáo theo mẫu khoa.
> Mọi tham số, tên nút, số lượng lấy từ mã nguồn tại commit hiện tại; sửa code thì sửa lại chương này.
> Hình đánh dấu `[CHỜ H18]` là sơ đồ Hùng đang vẽ.

## 3.1. Kiến trúc tổng thể

Hệ thống gồm bốn tầng, chạy trên một máy tính cá nhân (CPU) và gọi mô hình ngôn ngữ lớn qua API:

1. **Tầng dữ liệu**: văn bản luật đã chuẩn hóa, tách thành đoạn (chunk) theo cấu trúc Điều/Khoản, kèm khoảng hiệu lực; lưu ở tệp JSONL và trong cơ sở dữ liệu vector ChromaDB.
2. **Tầng truy xuất**: kết hợp tìm kiếm từ vựng (BM25) và tìm kiếm ngữ nghĩa (BGE-M3), hợp nhất bằng Reciprocal Rank Fusion, xếp hạng lại bằng cross-encoder, lọc theo ngày hiệu lực.
3. **Tầng tác tử**: một đồ thị trạng thái LangGraph điều phối định tuyến, truy xuất, đánh giá bằng chứng, sinh câu trả lời và kiểm chứng trích dẫn.
4. **Tầng giao tiếp**: API FastAPI và giao diện web NiceGUI.

<!-- Hình 3.1: assets/diagrams/architecture.png -->
**Hình 3.1.** Kiến trúc tổng thể của hệ thống.

Mô hình ngôn ngữ của tác tử là `gemini-3.1-flash-lite` (Google, gói miễn phí), gọi qua giao diện tương thích OpenAI. Mọi lượt gọi đi qua một lớp `LLM` dùng chung, có ba nhiệm vụ: lưu kết quả vào bộ đệm trên đĩa (cùng đầu vào thì không gọi lại, giúp chạy lại thí nghiệm không tốn hạn mức), giãn cách các lượt gọi theo giới hạn 15 lượt/phút của gói miễn phí, và đếm số lượt gọi cho từng bước. Embedding và reranker chạy cục bộ, không cần GPU.

## 3.2. Dữ liệu

### 3.2.1. Kho văn bản

Kho gồm 5 văn bản quy phạm pháp luật (Bảng 3.1). Bộ luật Lao động 2012 đã hết hiệu lực từ 01/01/2021 và được giữ lại có chủ đích để kiểm tra khả năng chọn đúng phiên bản theo thời điểm sự việc (RQ4).

**Bảng 3.1.** Văn bản trong kho và số đoạn sau khi tách.
<!-- nguồn: data/raw/laws.json; data/processed/chunks.jsonl, chunks_article.jsonl, chunks_fixed.jsonl -->

| Mã | Văn bản | Số hiệu | Hiệu lực | Số Điều | Số đoạn cấp Khoản | Số đoạn cố định |
|---|---|---|---|---|---|---|
| BLDS2015 | Bộ luật Dân sự 2015 | 91/2015/QH13 | từ 01/01/2017 | 689 | 1.673 | 513 |
| BLLD2012 | Bộ luật Lao động 2012 | 10/2012/QH13 | 01/05/2013 – 31/12/2020 | 242 | 686 | 222 |
| BLLD2019 | Bộ luật Lao động 2019 | 45/2019/QH14 | từ 01/01/2021 | 220 | 687 | 260 |
| LDN2020 | Luật Doanh nghiệp 2020 | 59/2020/QH14 | từ 01/01/2021 | 218 | 923 | 444 |
| LTM2005 | Luật Thương mại 2005 | 36/2005/QH11 | từ 01/01/2006 | 324 | 884 | 240 |
| | **Tổng** | | | **1.693** | **4.853** | **1.679** |

Văn bản dùng là bản gốc khi ban hành, chưa hợp nhất các lần sửa đổi, bổ sung; đây là một giới hạn của đề tài (mục 4.7).

### 3.2.2. Tiền xử lý

Văn bản tải từ Cơ sở dữ liệu quốc gia về văn bản pháp luật (vbpl.vn) ở dạng `.doc`, chuyển sang Markdown bằng MinerU, rồi phân tích cấu trúc thành JSON theo cây Phần → Chương → Mục → Điều → Khoản → Điểm (`data/legal_structure_parser.py`). Số Điều của mỗi văn bản được đối chiếu với mục lục; kiểm tra ngẫu nhiên 10 Điều mỗi văn bản về tên Điều, nội dung, số Khoản và số Điểm (`docs/data_check.md`).

### 3.2.3. Tách đoạn và siêu dữ liệu

Bộ tách (`src/ingestion/legal_chunker.py`) sinh ba loại đoạn:

- **Cấp Khoản** (mặc định): mỗi Khoản một đoạn; Điều không chia Khoản là một đoạn. Mã đoạn ghép từ mã văn bản, số Điều, số Khoản, ví dụ `BLLD2019_Dieu20_Khoan1`. Trung vị độ dài 38 từ.
- **Cấp Điều**: mỗi Điều một đoạn (trung vị 109 từ); dùng cho RQ2 và để trả toàn văn Điều.
- **Cố định**: cửa sổ trượt 200 từ, chồng lấp 40 từ, bỏ qua cấu trúc luật; là mốc so sánh của RQ2.

Mỗi đoạn mang siêu dữ liệu: tên văn bản, Chương, Mục, Điều, tên Điều, Khoản, Điểm, trạng thái và **khoảng hiệu lực** `effective_date`, `expiry_date` lấy từ `data/raw/laws.json`. Một đoạn có hiệu lực tại ngày *d* khi `effective_date ≤ d < expiry_date` (văn bản còn hiệu lực có `expiry_date` rỗng).

Từ ba loại đoạn trên, hệ thống tạo bốn chỉ mục (bốn biến thể của RQ2): Khoản kèm tiêu đề phân cấp (`clause_header`, mặc định), Khoản chỉ có nội dung (`clause_plain`), Điều kèm tiêu đề (`article`) và cố định (`fixed`). "Kèm tiêu đề" nghĩa là văn bản đem đi embedding được gắn thêm dòng "tên văn bản – Điều – tên Điều – Khoản" trước nội dung, để đoạn ngắn không mất ngữ cảnh.

## 3.3. Truy xuất căn cứ

Bộ truy xuất (`src/retrieval/retriever.py`) có bốn chế độ, cũng là bốn phương pháp so sánh ở RQ1:

1. **BM25** (`rank_bm25.BM25Okapi`): văn bản tách từ tiếng Việt bằng underthesea (từ ghép nối bằng dấu `_`), chữ thường, bỏ dấu câu.
2. **Dense**: embedding `BAAI/bge-m3` chuẩn hóa, độ đo cosine, lưu trong ChromaDB; giới hạn 2.048 token mỗi đoạn để giữ tốc độ trên CPU.
3. **Hybrid**: lấy 50 ứng viên từ mỗi nhánh rồi hợp nhất bằng Reciprocal Rank Fusion với hằng số *k* = 60: điểm của một đoạn là tổng 1/(60 + hạng) trên các danh sách.
4. **Hybrid + rerank** (mặc định): 10 ứng viên đầu sau RRF được chấm lại bằng cross-encoder `BAAI/bge-reranker-v2-m3`; con số 10 được chọn vì 20 ứng viên mất khoảng 11 giây mỗi câu trên CPU 16 nhân.

**Lọc theo hiệu lực.** Khi có ngày *d*, cả hai nhánh chỉ trả đoạn có hiệu lực tại *d*: nhánh dense lọc ngay trong truy vấn Chroma bằng hai trường số `effective_from`, `effective_to` (dạng YYYYMMDD, vì Chroma chỉ so sánh lớn hơn/nhỏ hơn trên số); nhánh BM25 lọc trên siêu dữ liệu. Ba chính sách lọc của RQ4:

- `event`: lọc theo ngày sự việc do router trích từ câu hỏi;
- `current`: chỉ lấy văn bản còn hiệu lực;
- `any`: không lọc, lấy mọi phiên bản.

Truy xuất **không** lọc theo lĩnh vực luật: nếu router đoán sai lĩnh vực thì truy xuất vẫn không bị kéo sai theo.

## 3.4. Tác tử Agentic-RAG

### 3.4.1. Đồ thị trạng thái

Tác tử là một đồ thị LangGraph (`src/agent/graph.py`) gồm 7 nút; trạng thái đi qua các nút chứa câu hỏi, loại câu, ngày sự việc, các truy vấn, bằng chứng, câu trả lời và dấu vết (trace).

<!-- Hình 3.2: assets/diagrams/Agentic Orchestration LangGraph cho hỏi đáp pháp luật.png -->
**Hình 3.2.** Đồ thị tác tử và các nhánh điều kiện.

**Bảng 3.2.** Các nút của tác tử.
<!-- nguồn: src/agent/nodes.py, src/agent/graph.py, src/agent/state.py -->

| Nút | Lượt LLM | Việc làm | Đi tiếp |
|---|---|---|---|
| `route` | 1 | Phân loại câu hỏi: tình huống (`situational`), tra cứu trực tiếp một Điều (`direct`), ngoài phạm vi (`out_of_scope`); trích ngày sự việc; với câu `direct` trích văn bản và số Điều | ngoài phạm vi → `refuse`; `direct` → `lookup_article`; còn lại → `retrieve` |
| `lookup_article` | 0 | Lấy toàn văn Điều được hỏi, nếu văn bản có hiệu lực tại ngày sự việc | có → `generate`; không → `retrieve` |
| `retrieve` | 0 | Tìm 5 đoạn bằng truy vấn mới nhất, lọc hiệu lực, gộp vào bằng chứng của các vòng trước (tối đa 15 đoạn, bỏ trùng) | không có gì → `refuse`; còn lại → `grade` |
| `grade` | 1 | Đánh giá bằng chứng đã đủ trả lời chưa; chưa đủ thì đề xuất truy vấn mới | đủ → `generate`; chưa đủ và còn lượt viết lại (tối đa 2) → `retrieve`; hết lượt → `refuse` |
| `generate` | 1 | Sinh câu trả lời tiếng Việt, mỗi câu gắn mã đoạn dạng `[BLLD2019_Dieu20_Khoan1]`; được phép trả "không đủ căn cứ" | không đủ căn cứ → `refuse`; còn lại → `verify` |
| `verify` | 0 hoặc 1 | Kiểm chứng trích dẫn (mục 3.4.2) | cần sinh lại → `generate`; xong → kết thúc |
| `refuse` | 0 | Trả lời từ chối kèm lý do: ngoài phạm vi, không tìm thấy căn cứ, hoặc căn cứ không đủ | kết thúc |

Một câu hỏi tình huống đi trọn luồng tốn khoảng 4 lượt gọi LLM (route, grade, generate, verify), nhiều hơn khi phải viết lại truy vấn hoặc sinh lại câu trả lời.

### 3.4.2. Kiểm chứng trích dẫn

Bước `verify` có hai lớp:

- **(a) Kiểm tra cú pháp** (không gọi LLM, luôn chạy ở mọi cấu hình): chuẩn hóa mã trích dẫn về đúng dạng trong kho, rồi gỡ mọi mã không nằm trong bằng chứng đã truy xuất. Lớp này bảo đảm hệ thống **không bao giờ** trả về trích dẫn tới một đoạn mà mô hình chưa được đọc.
- **(b) Kiểm tra ngữ nghĩa** (1 lượt LLM): mô hình nhận mọi cặp (câu, đoạn được trích) cùng tiêu đề Điều của đoạn, và chỉ ra cặp nào đoạn không hỗ trợ nội dung câu; các mã đó bị gỡ.

Câu nào mất hết trích dẫn sau hai lớp trên thì câu trả lời được sinh lại một lần, kèm danh sách câu chưa có căn cứ. Nếu sau lần sinh lại vẫn còn câu như vậy, câu đó được giữ nhưng gắn nhãn "(chưa có căn cứ)" để người đọc biết; câu trả lời không còn trích dẫn nào thì có thêm dòng ghi chú cuối.

Phiên bản đầu của lớp (b) chỉ đưa nội dung Khoản cho mô hình; thực nghiệm cho thấy nó gỡ nhầm nhiều trích dẫn đúng vì không biết Khoản thuộc Điều nào. Phiên bản hiện tại đưa thêm tên văn bản, số và tên Điều (so sánh ở mục 4.4).

### 3.4.3. Năm cấu hình thí nghiệm

Cùng một đồ thị phục vụ năm cấu hình của RQ3 bằng ba cờ bật/tắt (Bảng 3.3). Nút bị tắt vẫn có trong đồ thị nhưng không có cạnh nào dẫn tới, nên mọi cấu hình dùng chung mã nguồn và prompt, chỉ khác luồng đi.

**Bảng 3.3.** Năm cấu hình RQ3.
<!-- nguồn: src/agent/state.py CONFIGS -->

| Cấu hình | Router | Grade (viết lại truy vấn) | Verify (b) |
|---|---|---|---|
| `baseline` | tắt | tắt | tắt |
| `full` | bật | bật | bật |
| `no_router` | tắt | bật | bật |
| `no_grading` | bật | tắt | bật |
| `no_verify` | bật | bật | tắt |

Khi tắt router, câu hỏi luôn được coi là câu tình huống và không có ngày sự việc, nên truy xuất lọc theo văn bản còn hiệu lực. Verify (a) luôn chạy, kể cả ở `baseline`.

### 3.4.4. Dấu vết thực thi

Mỗi nút ghi một bước vào `trace`: tên nút, đầu ra rút gọn (bằng chứng chỉ giữ mã đoạn), thời gian xử lý và số lượt gọi LLM. Thời gian đã trừ phần chờ giãn cách của gói API miễn phí, nên phản ánh độ trễ của chính hệ thống. Trace vừa hiển thị trên giao diện (dòng thời gian các bước), vừa là dữ liệu cho đo độ trễ và phân tích lỗi ở Chương 4.

## 3.5. API và giao diện

**API** (`src/api/main.py`, FastAPI) theo định dạng ở Phụ lục A.5 của đề cương:

- `POST /api/ask` nhận câu hỏi (1–1.000 ký tự) và tên cấu hình (mặc định `full`); trả câu trả lời, trạng thái từ chối, danh sách trích dẫn (mã đoạn, văn bản, Điều, Khoản, nội dung), các đoạn đã truy xuất và trace.
- `GET /api/article/{law_id}/{article}` trả toàn văn một Điều để giao diện hiển thị khi người dùng bấm vào trích dẫn.
- `GET /health` trả trạng thái và tên mô hình.

Tác tử được nạp một lần khi khởi động. Các câu hỏi được phục vụ tuần tự (khóa), vì bộ đếm lượt gọi, bộ giãn cách và bộ đệm của lớp `LLM` dùng chung giữa các yêu cầu.

**Giao diện** (`src/ui/web/`, NiceGUI, do Hùng xây dựng) gồm khung hội thoại, thẻ trích dẫn mở được toàn văn Điều, thẻ hiệu lực văn bản và dòng thời gian các bước của tác tử (Hình 3.3–3.5).

<!-- Hình 3.3: assets/screenshots_nicegui/nicegui_02_answered_citations.png -->
<!-- Hình 3.4: assets/screenshots_nicegui/nicegui_03_validity_and_timeline.png -->
<!-- Hình 3.5: assets/screenshots_nicegui/nicegui_06_mobile_390x844.png -->
**Hình 3.3–3.5.** Câu trả lời kèm trích dẫn; hiệu lực văn bản và các bước của tác tử; giao diện trên điện thoại.

<!-- Hình 3.6: assets/diagrams/usecase.png [CHỜ H18] -->
<!-- Hình 3.7: assets/diagrams/sequence.png [CHỜ H18] -->
**Hình 3.6–3.7.** Sơ đồ use case và sơ đồ tuần tự xử lý một câu hỏi. `[CHỜ H18]`

## 3.6. Xử lý lỗi

**Bảng 3.4.** Các tình huống lỗi và cách xử lý.
<!-- nguồn: spec mục 6; src/generation/llm.py, src/agent/nodes.py, src/api/main.py -->

| Tình huống | Cách xử lý |
|---|---|
| API mô hình báo quá hạn mức (429) hoặc quá tải (5xx) | Thư viện tự chờ lũy tiến rồi thử lại: 8 lần khi chạy thực nghiệm; 2 lần khi phục vụ API, để người dùng nhận thông báo trong vài chục giây thay vì chờ tới 3 phút |
| Hết số lần thử khi phục vụ API | Trả mã 503 với thông báo "Dịch vụ mô hình ngôn ngữ đang quá tải hoặc tạm thời không khả dụng…", ghi chi tiết vào log máy chủ |
| Mô hình trả JSON hỏng | Thử lại một lần kèm nhắc "chỉ trả về JSON"; vẫn hỏng thì dùng mặc định an toàn: router coi là câu tình huống, grade coi là đủ bằng chứng, verify (b) không gỡ gì |
| Ngày sự việc sai định dạng; văn bản hoặc Điều do router trích không có trong kho | Bỏ ngày; câu `direct` rơi về truy xuất thường |
| Đầu vào API sai (rỗng, quá dài, cấu hình lạ) | Trả mã 422 |
| Truy xuất không có kết quả, hoặc grade kết luận không đủ sau 2 lần viết lại | Từ chối, nêu lý do |
| Mô hình gắn mã trích dẫn không có trong bằng chứng | Verify (a) gỡ trước khi trả về; không có ngoại lệ |
| Chạy thực nghiệm bị dừng giữa chừng (hết hạn mức) | Mỗi kết quả ghi ngay một dòng JSONL; chạy lại thì bỏ qua câu đã xong. Điểm chấm gắn với mã băm câu trả lời, nên câu được chạy lại sẽ được chấm lại |
