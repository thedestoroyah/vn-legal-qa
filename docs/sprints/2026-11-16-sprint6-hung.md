# Sprint 6 — Việc của Hùng (16/11 – 27/11/2026)

Tài liệu gồm các **thẻ việc**. Mỗi thẻ có đủ mục tiêu, file vào/ra, các bước và điều kiện "xong khi". Có thể dán nguyên một thẻ cho agent CLI hoặc web chat; dán kèm `AGENTS.md` nếu công cụ không tự đọc.

- Bối cảnh chung, quy tắc, lệnh chạy: **`AGENTS.md`** (đọc trước).
- Phần Đạt làm song song (Docker, README, sửa lỗi nhỏ, rà soát báo cáo): `docs/superpowers/plans/2026-11-16-sprint6-dat.md`.
- Hạn nộp **23:59 04/12/2026**; báo cáo hoàn chỉnh **27/11**; dự phòng 28/11 – 03/12; nộp 03/12.

## Đọc trước

- Thẻ Sprint 5 còn dở (H17, H18, H12, H21 trong `docs/sprints/2026-11-05-sprint5-hung.md`) làm xong trước khi bắt đầu H23, vì H23 ghép các chương đó.
- Bản nháp hiện có trong `docs/report/`: `chuong1_draft.md` (Hùng), `chuong3_draft.md`, `chuong4_draft.md` (Đạt). Hình: `docs/report/figures/` (biểu đồ RQ1–RQ4), `assets/diagrams/`, `assets/screenshots_nicegui/`.
- Thực nghiệm đã xong, **không chạy lại**. Số liệu chỉ lấy từ `eval/results/*.md` hoặc từ Chương 4 (mỗi bảng có comment ghi file nguồn).

## Thứ tự và hạn

| Thẻ | Việc | Hạn | Phụ thuộc |
|---|---|---|---|
| H22 | Giao diện bớt "kiểu AI", chụp lại ảnh | 19/11 | — |
| H23 | Ghép báo cáo theo mẫu TDTU | 24/11 | H12, H17, H21 (Sprint 5); H22 (ảnh mới) |
| H24 | Slide bảo vệ 15–20 slide | 26/11 | H23 |
| H25 | Video demo 3–5 phút | 26/11 | H22 |

Nghiệm thu Sprint 6 (27/11): báo cáo hoàn chỉnh theo mẫu TDTU (đã qua rà soát của Đạt), slide bảo vệ, video demo.

## Quy trình chung

- Luôn `git pull` trước khi làm. Commit nhỏ theo từng thẻ: `feat(ui): ...`, `docs: ...`.
- **Không sửa** code của Đạt: `src/agent/`, `src/api/`, `src/generation/`, `src/retrieval/`, `src/ingestion/`, `eval/*.py`; không sửa `eval/results/`, `eval/*cases.json`. Thấy lỗi thì báo Đạt.
- File của Hùng: `src/ui/`, `tests/test_nicegui_web.py`, `assets/`, `docs/report/` (trừ `chuong3_draft.md`, `chuong4_draft.md`: góp ý cho Đạt), slide và video.
- Trước khi commit phần giao diện: `pytest -q` phải pass hết.

---

## H22 — Giao diện bớt "kiểu AI"

**Mục tiêu:** giao diện trông như một công cụ tra cứu pháp luật nghiêm túc, không như sản phẩm demo AI. Chức năng giữ nguyên.

**Các thay đổi** (trong `src/ui/web/`; mỗi mục một commit nhỏ):
1. **Bỏ nút "Hữu ích / Chưa chuẩn"** (`components/chat_message.py`, khoảng dòng 180–190, và `set_feedback` trong `pages/chat.py`): phản hồi không được lưu ở đâu, nút chỉ để trang trí. Bỏ trường `feedback` của `Turn` nếu không còn dùng; sửa test liên quan trong `tests/test_nicegui_web.py`.
2. **Bỏ gradient** ở bong bóng câu hỏi (`static/styles.css`, `.user-bubble`, khoảng dòng 352): dùng một màu nền đặc (`#1e3a8a`).
3. **Bỏ hiệu ứng động** `@keyframes agentPulse`, `fadeInUp` và các `animation:` dùng chúng; giữ `transition` ngắn khi rê chuột.
4. **Giảm bóng đổ**: các `box-shadow` có độ mờ ≥ 10px đổi thành viền 1px (`border: 1px solid #e2e8f0`), trừ thanh bên trượt ra trên điện thoại.
5. **Đổi nhãn**: "Trợ lý pháp luật Agentic-RAG" → "Câu trả lời"; dòng phụ dưới tên ứng dụng "Agentic-RAG · 5 văn bản luật" → "5 văn bản luật · tra cứu theo hiệu lực". Tên kỹ thuật (Agentic-RAG, LLM) chỉ giữ trong phần "Các bước tác tử" và trang thông tin.
6. Giữ nguyên: thẻ trích dẫn, panel toàn văn Điều, thẻ hiệu lực, dòng thời gian các bước, giao diện điện thoại.
7. **Nhãn riêng khi dùng dữ liệu dự phòng** (`components/sidebar.py`, khoảng dòng 123). Chạy venv mà không nối được API thì giao diện vẫn hiện "Đã kết nối" và tự dùng dự phòng: có key thì tác tử chỉ truy xuất bằng BM25 (dòng `Model` vẫn ghi gemini nên không phân biệt được), không có key thì trả câu ghi sẵn hoặc đoạn BM25 chưa kiểm chứng. Khi `client._using_fallback` đúng, hiện nhãn "Dữ liệu dự phòng" thay cho "Đã kết nối". (Docker đã tắt dự phòng bằng `UI_LOCAL_FALLBACK=0`, Đạt đã sửa `main.py`.)
8. **Sửa gợi ý lỗi** (`api/client.py`, khoảng dòng 129): "đợi vài giây rồi bấm Thử lại" chỉ đúng với lỗi 503. Với lỗi 500 (chỉ mục lỗi, thử lại không có tác dụng) thì bỏ gợi ý này.

**Xong khi:**
- `pytest -q` pass hết.
- Chạy `README.md` mục 1 một lượt trên Windows (PowerShell, Docker Desktop): ghi lại mọi chỗ khác với README và báo Đạt.
- Chạy API + giao diện (lệnh trong `AGENTS.md`), hỏi 4 câu của H25: hiển thị đúng như trước, không còn nút đánh giá, gradient, hiệu ứng nhấp nháy.
- Chụp lại 6 ảnh trong `assets/screenshots_nicegui/` (ghi đè đúng tên file cũ, cùng kích thước 1440×900 / 1366×768 / 1024×768 / 390×844).
- Đạt xem ảnh và đồng ý.

## H23 — Ghép báo cáo theo mẫu TDTU

**Đầu vào:** `docs/report/chuong1_draft.md` … `chuong5_draft.md`; khung `docs/report/final_52300098_52300106.docx` (Hùng đã tạo theo mẫu khoa); mẫu gốc của khoa `TemplateCacMonDuAnVaThucTap_KhoaCNTT.dotx` (Đạt gửi nếu cần); danh mục tài liệu: mục 12 `docs/managements/Đề cương DACNTT.md` (đã tra lại nguồn ngày 03/11, có DOI).

**Các bước:**
1. Chép nội dung 5 chương từ Markdown vào docx, dùng đúng style của mẫu (Heading 1/2/3, đoạn thường, chú thích hình/bảng). Số liệu, bảng chép nguyên văn, **không gõ lại số**.
2. Hình: biểu đồ `docs/report/figures/rq1.png`, `rq2.png`, `rq3_diff.png`, `rq4.png`; sơ đồ `assets/diagrams/` (kiến trúc, activity, đồ thị tác tử, use case, sequence); ảnh giao diện mới (H22). Chú thích dạng "Hình 4.1. …" đúng như trong bản Markdown.
3. Phần đầu: bìa (tên đề tài nguyên văn mục 1 đề cương), lời cảm ơn, cam đoan, tóm tắt (tiếng Việt và tiếng Anh, khoảng 200 từ mỗi bản, tóm tắt từ Chương 5), mục lục, danh mục hình, danh mục bảng, danh mục từ viết tắt (RAG, LLM, BM25, RRF, HĐLĐ, BLLĐ, BLDS, LDN, LTM…) — dùng chức năng mục lục tự động của Word.
4. Tài liệu tham khảo: chép từ mục 12 đề cương, định dạng APA 7 theo mẫu khoa; mọi tài liệu trong danh mục phải được trích trong thân bài và ngược lại (dùng tìm kiếm "và cộng sự" / tên tác giả để đối chiếu).
5. Bỏ mọi ghi chú nháp (`> Bản nháp …`, `<!-- nguồn: … -->`, `[CHỜ …]`, `[CẦN KIỂM TRA]`).

**Xong khi:** gửi Đạt file docx ngày 24/11; mục lục, danh mục hình/bảng cập nhật được; không còn ghi chú nháp; Đạt rà soát xong (Task 5 của Đạt) thì sửa theo góp ý trước 27/11.

## H24 — Slide bảo vệ (15–20 slide)

**Thiết kế:** cùng phong cách slide báo cáo tuần (`docs/managements/Week 02.11-08.11/build_pptx.js`: Arial, xanh `2C5EAD`/`1591DC`, thẻ nền `EAF4FC`, logo TDTU). Có thể dựng bằng script như báo cáo tuần hoặc làm tay trên PowerPoint.

**Dàn ý:** vấn đề (2) → mục tiêu và 4 câu hỏi nghiên cứu (1) → dữ liệu và tập kiểm thử (2) → kiến trúc và tác tử (3) → demo (1, nhúng hoặc dẫn link video H25) → kết quả RQ1–RQ4 (4, dùng 4 biểu đồ trong `docs/report/figures/`) → phân tích lỗi và giới hạn (2) → kết luận, hướng phát triển (1) → cảm ơn. Mỗi slide có lời thuyết trình (notes), tổng khoảng 10–12 phút.

**Xong khi:** gửi Đạt ngày 26/11; mọi con số trên slide có trong Chương 4; hai người tập thuyết trình trọn một lượt trong khoảng 12 phút.

## H25 — Video demo 3–5 phút

**Chuẩn bị:** dùng giao diện sau H22; mạng ổn định (hotspot, không dùng mạng thư viện vì chậm hơn); **thử trước 1 câu** — nếu Gemini báo quá tải (503) thì chờ, không quay lúc đang lỗi. Chạy API và giao diện như `AGENTS.md`. **Trước khi quay, mở `http://localhost:8000/health` phải thấy `"status":"ok"`:** API chưa chạy thì giao diện vẫn hiện "Đã kết nối" nhưng dùng dự phòng (chỉ BM25), câu trả lời trong video sẽ không phải của hệ thống đầy đủ.

**4 kịch bản** (gõ đúng các câu sau):
1. Tình huống: "Bên mua trả tiền chậm có phải trả lãi không?" — bấm một thẻ trích dẫn để mở toàn văn Điều.
2. Có mốc thời gian: "Năm 2020, người lao động nghỉ việc phải báo trước bao nhiêu ngày nếu làm hợp đồng không xác định thời hạn?" — chỉ ra căn cứ là BLLĐ 2012 (đúng phiên bản theo năm 2020) và thẻ hiệu lực "Hết hiệu lực".
3. Ngoài phạm vi: "Thủ tục ly hôn đơn phương cần giấy tờ gì?" — hệ thống từ chối, nêu phạm vi hỗ trợ.
4. Tra cứu trực tiếp: "Theo Bộ luật Lao động 2012, Điều 104 quy định thời giờ làm việc bình thường như thế nào?" — mở phần "Các bước tác tử" cho thấy bước tra cứu thẳng Điều.

**Yêu cầu:** quay màn hình 1920×1080, có lời thuyết minh hoặc phụ đề tiếng Việt; cắt bỏ phần chờ dài (giữ một đoạn ngắn cho thấy hệ thống đang xử lý); lưu `.mp4`, không commit vào git (file lớn) — gửi link Drive cho Đạt.

**Xong khi:** video 3–5 phút đủ 4 kịch bản, câu trả lời trong video khớp hệ thống hiện tại; Đạt xem và đồng ý.
