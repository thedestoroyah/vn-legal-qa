HỆ THỐNG HỎI ĐÁP PHÁP LUẬT VIỆT NAM DỰA TRÊN AGENTIC-RAG
VỚI TRUY XUẤT CĂN CỨ THEO HIỆU LỰC VÀ KIỂM CHỨNG TRÍCH DẪN

Dự án Công nghệ thông tin (504091) - Đề tài ĐA127 - Trường Đại học Tôn Đức Thắng
Giảng viên hướng dẫn: PGS.TS. Lê Anh Cường
Sinh viên: Phạm Huỳnh Quốc Đạt (52300098), Hoàng Sinh Hùng (52300106)

Hệ thống trả lời câu hỏi pháp luật tiếng Việt trên 5 văn bản: Bộ luật Dân sự 2015,
Bộ luật Lao động 2012 và 2019, Luật Doanh nghiệp 2020, Luật Thương mại 2005. Căn cứ được
truy xuất theo văn bản có hiệu lực tại thời điểm sự việc; mọi trích dẫn được kiểm chứng
trước khi trả về. Hướng dẫn đầy đủ hơn nằm trong README.md (cùng thư mục).


1. NỘI DUNG THƯ MỤC
-------------------
  src/            mã nguồn: ingestion (tách đoạn, lập chỉ mục), retrieval (BM25, dense, RRF,
                  rerank, lọc hiệu lực), generation (LLM, prompt, trích dẫn), agent (đồ thị
                  LangGraph), api (FastAPI), ui (giao diện web NiceGUI)
  data/           văn bản luật đã cấu trúc hóa và các đoạn (chunk) đã tách
  eval/           tập kiểm thử 209 câu, mã đánh giá, kết quả thực nghiệm (eval/results/)
  tests/          kiểm thử tự động (pytest)
  docs/           kế hoạch, thiết kế, bản nháp các chương báo cáo
  assets/         sơ đồ (draw.io) và ảnh giao diện
  chroma_db.zip   chỉ mục vector đã nạp sẵn (73 MB, 4 biến thể); giải nén ra chroma_db/
  Dockerfile, docker-compose.yml   chạy hệ thống bằng Docker
  requirements.txt                 thư viện Python (phiên bản cố định)

Không kèm: file .env chứa API key, thư mục .venv, bộ đệm .cache, mô hình BGE-M3 và
bge-reranker-v2-m3 (tự tải ở lần chạy đầu).


2. CẦN CHUẨN BỊ
---------------
  - Một API key Gemini miễn phí, lấy tại https://aistudio.google.com
    (mô hình gemini-3.1-flash-lite; gói miễn phí khoảng 500 lượt gọi/ngày, đôi khi báo
    quá tải 503: đợi vài phút rồi hỏi lại).
  - Cách A: Docker có Compose. Cách B: Python 3.14.
  - RAM trống từ 4 GB; đĩa trống khoảng 12 GB. Không cần GPU.
  - Lần chạy đầu tải khoảng 7 GB mô hình từ Hugging Face, có thể mất nhiều phút.


3. CÁCH A: CHẠY BẰNG DOCKER (khuyên dùng)
-----------------------------------------
Tại thư mục này (Linux/macOS):

  cp .env.example .env          (mở .env, điền LLM_API_KEY=<key Gemini>)
  mkdir -p .cache/llm
  unzip chroma_db.zip
  docker compose up --build

Windows PowerShell:

  Copy-Item .env.example .env   (mở .env, điền LLM_API_KEY)
  mkdir .cache/llm -Force
  Expand-Archive chroma_db.zip -DestinationPath .
  docker compose up --build

Mở giao diện: http://localhost:8080 (API: http://localhost:8000, tài liệu API ở /docs).
Tắt: Ctrl+C rồi docker compose down.
Lỗi khởi động (thiếu key, thiếu chỉ mục): xem docker compose logs api.


4. CÁCH B: CHẠY BẰNG PYTHON
---------------------------
  python -m venv .venv
  source .venv/bin/activate                 (Windows: .venv\Scripts\Activate.ps1)
  pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu
  pip install -r requirements.txt
  cp .env.example .env                      (điền LLM_API_KEY)
  unzip chroma_db.zip

  uvicorn src.api.main:app --port 8000      (cửa sổ thứ nhất: API)
  python -m src.ui.web.main                 (cửa sổ thứ hai: giao diện, http://127.0.0.1:8080)

Hỏi từ dòng lệnh, không cần giao diện:
  python -m src.agent.run "Bên mua trả tiền chậm có phải trả lãi không?"

Chạy kiểm thử (không cần key, mô hình hay chỉ mục):
  pytest -q


5. CÂU HỎI THỬ
--------------
  - Tình huống:        Bên mua trả tiền chậm có phải trả lãi không?
  - Có mốc thời gian:  Năm 2020, người lao động nghỉ việc phải báo trước bao nhiêu ngày nếu
                       làm hợp đồng không xác định thời hạn?   (căn cứ là BLLĐ 2012)
  - Ngoài phạm vi:     Thủ tục ly hôn đơn phương cần giấy tờ gì?   (hệ thống từ chối)
  - Tra cứu trực tiếp: Điều 357 Bộ luật Dân sự 2015 quy định gì?

Mỗi câu mất khoảng 10-30 giây (khoảng 4 lượt gọi LLM, xếp hạng lại chạy trên CPU).


6. TÁI LẬP SỐ LIỆU TRONG BÁO CÁO
--------------------------------
Kết quả thô có sẵn trong eval/results/*.jsonl. Các lệnh tạo lại bảng RQ3, RQ4 chỉ đọc các
file này (không cần key, không gọi LLM); RQ1, RQ2 chạy lại truy xuất trên CPU, cần
chroma_db/. Bảng đối chiếu từng bảng trong báo cáo với lệnh tương ứng: README.md, mục 4.
Ví dụ:
  python -m eval.evaluate --rq rq1
  python -m eval.agent_eval report --rq rq3 --common --ci


7. KHÔNG CÓ chroma_db.zip
-------------------------
Tự nạp chỉ mục (khoảng 2 giờ trên CPU cho biến thể mặc định):
  python -m src.ingestion.index --variant clause_header --rebuild
(Docker: docker compose run --rm api python -m src.ingestion.index --variant clause_header --rebuild)
