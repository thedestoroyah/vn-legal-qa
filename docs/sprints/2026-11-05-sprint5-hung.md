# Sprint 5 — Việc của Hùng (05/11 – 15/11/2026)

Tài liệu gồm các **thẻ việc**. Mỗi thẻ có đủ mục tiêu, file vào/ra, các bước và điều kiện "xong khi". Có thể dán nguyên một thẻ cho agent CLI hoặc web chat để nhờ hỗ trợ; dán kèm `AGENTS.md` nếu công cụ không tự đọc.

- Bối cảnh chung, quy tắc tập kiểm thử, lệnh chạy: **`AGENTS.md`** (đọc trước).
- Phần Đạt làm song song: `docs/superpowers/plans/2026-11-05-sprint5-dat.md`.
- Lịch mới: hạn nộp **23:59 04/12/2026**; đóng băng tính năng 12/11; Sprint 6 16/11–27/11; dự phòng 28/11–03/12.

## Đọc trước

Cảm ơn Hùng về giao diện NiceGUI, sơ đồ activity/kiến trúc, `rubric.md`, `judge_review.md`, bản nháp Chương 1 và câu M_017. Đạt đã:
- Chạy lại M_017 cho 5 cấu hình RQ3 và 3 chính sách RQ4, chấm lại; cả 8 lượt trích đúng `BLLD2019_Dieu20_Khoan1`.
- Sửa `src/ingestion/index.py`: commit "fix Chroma metadata" bỏ giá trị None làm hỏng test `test_reindex_without_rebuild_clears_stale_fields` (khi nạp lại, trường đã bỏ như `expiry_date` vẫn còn giá trị cũ). Giờ giữ cách bỏ None của Hùng và xóa id cũ trước khi upsert. Lần sau thấy test hỏng thì báo Đạt, đừng sửa test.
- Chạy xong tập giữ riêng 30 câu (M_038–M_067) và RQ1/RQ2 trên 77 câu Zalo. Số liệu trong `eval/results/*.md`.
- H14: Đạt đã chấm 20 câu (`grading_rq3_dat.csv`). Hùng **không cần** chấm nữa.

## Thứ tự và hạn

| Thẻ | Việc | Hạn | Phụ thuộc |
|---|---|---|---|
| H17 | Cập nhật số liệu Chương 1 | 07/11 | — |
| H19 | Kiểm giao diện NiceGUI với API thật, cùng Đạt | 07/11 | Task 1 của Đạt |
| H18 | Sơ đồ use case và sequence | 09/11 | — |
| H12 | Bản nháp Chương 2 (thẻ Sprint 3) | 10/11 | — |
| H21 | Bản nháp Chương 5 | 15/11 | Chương 4 của Đạt (bản nháp) |

Nghiệm thu Sprint 5 (15/11): có bản nháp Chương 1, 2, 5; đủ 4 sơ đồ; giao diện chạy với API thật trên máy Đạt.

## Quy trình chung

- Luôn `git pull` trước khi làm. Commit nhỏ theo từng thẻ, dạng `docs: ...`, `feat(ui): ...`.
- **Không sửa** code của Đạt: `src/agent/`, `src/api/`, `src/generation/`, `src/retrieval/`, `src/ingestion/`, `eval/*.py`, `tests/` của các phần đó. Thấy lỗi thì báo Đạt.
- **Không sửa** `eval/manual_cases.json`, `eval/test_cases.json`, `eval/results/subset_*.json` mà chưa báo Đạt: sửa một câu đã chạy là phải chạy lại và tốn quota (xem `AGENTS.md`).
- File của Hùng: `src/ui/`, `assets/`, `docs/report/chuong1_draft.md`, `chuong2_draft.md`, `chuong5_draft.md`.
- Bản nháp viết Markdown trong `docs/report/`, cùng quy ước với `chuong1_draft.md`. Tài liệu ngoài mục 12 đề cương ghi `[CẦN KIỂM TRA]`. Số liệu chỉ lấy từ `eval/results/*.md`, không lấy từ chat hay trí nhớ của AI.

---

## H17 — Cập nhật số liệu Chương 1 (Đạt làm thay ngày 10/11, Hùng không cần làm)

**Vấn đề:** `docs/report/chuong1_draft.md` viết ngày 29/10, tập kiểm thử khi đó 179 câu. Nay là 209 câu.

**Các bước:**
1. Mục 1.3.2 (khoảng dòng 76–80): sửa thành 209 câu = Zalo 77 + tổng hợp 65 + tự soạn 67 (15 tình huống, 32 có mốc thời gian, 15 tra cứu trực tiếp, 5 ngoài phạm vi). Đối chiếu bằng lệnh:
   ```bash
   python -c "import json,collections; c=json.load(open('eval/test_cases.json',encoding='utf-8')); print(len(c), collections.Counter(x['source'] for x in c), collections.Counter((x['source'],x['type']) for x in c if x['source']=='manual'))"
   ```
2. Thêm 1–2 câu: 30 câu tự soạn (M_038–M_067) là **tập giữ riêng**, soạn và chốt trước khi chạy hệ thống (`docs/superpowers/specs/2026-11-03-heldout-prereg.md`), để kiểm tra kết quả không bị "khớp" với tập đã dùng khi chỉnh prompt.
3. Mục 1.4: lịch 6 sprint đã sửa thành 09/10–04/12/2026; kiểm lại.
4. Lập danh sách mọi chỗ `[CẦN KIỂM TRA]` (hiện có 2) ở cuối file, mục "Cần Đạt tra", mỗi dòng: tài liệu, chỗ dùng.

**Xong khi:** không còn số 179, 37, "12 câu có mốc thời gian" trong file; lệnh ở bước 1 in ra đúng các số đã viết.

## H19 — Kiểm giao diện NiceGUI với API thật (cùng Đạt, trên máy Đạt)

**Vì sao:** ngày 03/11 Đạt chạy thử thì Gemini đang quá tải (503). API thử lại 8 lần, mất 174 giây mới báo lỗi, nên giao diện hết thời gian chờ (180 giây) và chỉ hiện "Máy chủ trả lời quá lâu". Task 1 của Đạt giảm số lần thử lại của API xuống 2.

**Các bước** (sau khi Đạt xong Task 1):
1. Terminal 1: `uvicorn src.api.main:app --port 8000`. Terminal 2: `python -m src.ui.web.main`, mở http://127.0.0.1:8080.
2. Hỏi lần lượt 4 câu (cũng là 4 kịch bản video demo ở Sprint 6):
   - Tình huống: "Bên mua trả tiền chậm có phải trả lãi không?"
   - Có mốc thời gian: "Năm 2020, người lao động nghỉ việc phải báo trước bao nhiêu ngày nếu làm hợp đồng không xác định thời hạn?"
   - Ngoài phạm vi: "Thủ tục ly hôn đơn phương cần giấy tờ gì?"
   - Tra cứu trực tiếp: "Điều 357 Bộ luật Dân sự 2015 quy định gì?"
3. Với mỗi câu: bấm thẻ trích dẫn mở toàn văn Điều; mở dòng thời gian các bước của tác tử (agent timeline).
4. Tắt API rồi hỏi tiếp.
5. Chụp lại ảnh nào khác với `assets/screenshots_nicegui/` (ghi đè đúng tên file cũ).

**Xong khi:**
- Câu 1, 2, 4 có trả lời và trích dẫn; câu 2 trích BLLĐ 2012; câu 3 bị từ chối, giao diện hiện lý do.
- Bước 4 hiện thông báo không kết nối được máy chủ, không hiện traceback.
- Lỗi phát hiện ở phía giao diện thì Hùng sửa trong `src/ui/web/` (kèm test trong `tests/test_nicegui_web.py`); lỗi phía API thì ghi lại gửi Đạt.

## H18 — Sơ đồ use case và sequence (Đạt làm thay ngày 10/11, Hùng không cần làm)

**Đã có:** `assets/diagrams/activity.*`, `architecture.png`, sơ đồ LangGraph. **Còn thiếu** 2 sơ đồ cho Chương 3:

1. **Use case** (`assets/diagrams/usecase.drawio` + `.png`): tác nhân Người dùng; các use case: đặt câu hỏi, xem trích dẫn và toàn văn Điều, xem các bước của tác tử, chọn cấu hình (nếu giao diện có), nhận thông báo từ chối. Tác nhân phụ: dịch vụ LLM (Gemini).
2. **Sequence** (`assets/diagrams/sequence.drawio` + `.png`): Người dùng → NiceGUI → FastAPI `POST /api/ask` → Agent (route → retrieve/lookup_article → grade → generate → verify) → Retriever (Chroma + BM25) → LLM; trả `AskResponse` theo Phụ lục A.5; nhánh lỗi: LLM 503 → API 503 → giao diện hiện thông báo.

Tên nút, tên endpoint, tên trường lấy đúng từ code (`src/agent/graph.py`, `src/api/main.py`) và Phụ lục A.5.

**Xong khi:** 2 file `.drawio` và 2 file `.png` (rộng ≥ 1600 px, chữ đọc được khi in A4) trong `assets/diagrams/`; Đạt xem và không có tên nào lệch với code.

## H20 — Gán nhãn lỗi 20 câu (Đạt đảm nhận từ 03/11, Hùng không cần làm)

Giữ lại mô tả dưới đây làm hướng dẫn gán nhãn.

**Đầu vào:** `eval/results/errors_rq3.csv` (Đạt tạo ngày 06/11). Mỗi dòng là một câu cấu hình `full` trả lời chưa tốt, kèm câu hỏi, đáp án mẫu, căn cứ chuẩn (`gold`), căn cứ đã trích (`cited`), loại định tuyến (`route`), câu trả lời, và gợi ý tự động (`hints`).

**Nhãn** (cột `category`, nhiều nhãn cách nhau bằng `;`):

| Nhãn | Khi nào |
|---|---|
| `truy_xuat_sai_dieu` | Không lấy được Điều đúng, dù đúng văn bản |
| `sai_van_ban` | Lấy nhầm sang văn bản khác (vd hỏi lao động, trích Bộ luật Dân sự) |
| `sai_phien_ban` | Đúng nội dung nhưng sai phiên bản theo thời gian (BLLĐ 2012 ↔ 2019) |
| `trich_dan_khong_ho_tro` | Mã trích dẫn không chứa nội dung của câu gắn nó |
| `dinh_tuyen_sai` | Router xếp nhầm loại câu (vd câu tra cứu trực tiếp bị coi là tình huống), hoặc trích sai ngày sự việc |
| `tu_choi_nham` | Câu trong phạm vi nhưng hệ thống từ chối |
| `dap_an_mau_tranh_cai` | Hệ thống trả lời hợp lý; đáp án mẫu hoặc căn cứ chuẩn mới là chỗ có vấn đề |
| `tra_loi_thieu_y` | Trích đúng nhưng câu trả lời bỏ điều kiện, con số mà câu hỏi cần |
| `trich_them_lien_quan` | Trích thêm Điều có liên quan ngoài căn cứ chuẩn (chỉ số trừ điểm, không phải lỗi thật) |
| `bo_cham_qua_chat` | Bộ chấm trừ điểm vì thiếu chi tiết mà câu hỏi không hỏi tới (rubric R5) |
| `khong_phai_loi` | Chỉ số báo lỗi nhưng xem kỹ thì câu trả lời hoặc việc từ chối là hợp lý |
| `khac` | Không thuộc loại nào ở trên (ghi rõ trong `note`) |

**Các bước:**
1. Với mỗi dòng: đọc câu hỏi, câu trả lời, `gold` và `cited`; mở toàn văn Điều khi cần (`python -m eval.show_article BLLD2019 35`: mã văn bản rồi số Điều; hoặc panel trên giao diện).
2. Điền `category` và một câu lý do ở `note`. Gợi ý ở `hints` chỉ là gợi ý từ chỉ số, không phải đáp án.
3. **Không sửa** các cột khác, không thêm/xóa dòng. Câu thấy đáp án mẫu sai thì gán `dap_an_mau_tranh_cai` và báo Đạt, không sửa `manual_cases.json`.

**Xong khi:** đủ 20 dòng có `category`; lệnh `python -m eval.error_analysis report` chạy không báo lỗi; gửi Đạt duyệt.

## H12 — Bản nháp Chương 2 (cơ sở lý thuyết)

Giữ nguyên nội dung thẻ H12 trong `docs/sprints/2026-10-16-sprint3-hung.md` (8 mục: BM25, dense/BGE-M3, RRF, cross-encoder, RAG, Agentic-RAG, LangGraph, đặc thù văn bản luật Việt Nam). Thay đổi duy nhất: viết vào `docs/report/chuong2_draft.md` (Markdown, như Chương 1), không cần gửi link.

**Xong khi:** đủ 8 mục, mỗi mục có 1–2 câu nối với thiết kế ở Chương 3; mọi trích dẫn có trong mục 12 đề cương hoặc có nhãn `[CẦN KIỂM TRA]`; công thức BM25 và RRF viết đúng ký hiệu trong nguồn gốc.

## H21 — Bản nháp Chương 5 (kết luận, hạn chế, hướng phát triển) (Đạt làm thay ngày 10/11, Hùng không cần làm)

**Đầu vào:** bản nháp Chương 4 của Đạt (`docs/report/chuong4_draft.md`, dự kiến 13–14/11), file chốt trước `docs/superpowers/specs/2026-11-03-heldout-prereg.md`.

**Các mục** (khoảng 2–3 trang, `docs/report/chuong5_draft.md`):
1. Kết luận: trả lời ngắn từng RQ1–RQ4 bằng đúng số trong Chương 4; nêu cả giả thuyết không được ủng hộ (vd RQ4: `event` hơn `current` có ý nghĩa, hơn `any` thì chưa).
2. Hạn chế: chép ý từ mục 4.7 của Chương 4, viết gọn (prompt chỉnh sau khi thấy tập kiểm thử, một người chấm tay, bộ chấm dễ dãi, cỡ mẫu, văn bản chưa hợp nhất sửa đổi, quota API miễn phí).
3. Hướng phát triển: mỗi hạn chế một hướng cụ thể (vd hợp nhất văn bản sửa đổi, thêm Nghị định/Thông tư, tập dev riêng để chỉnh prompt, nhiều người chấm).

**Xong khi:** mỗi con số trong Chương 5 có trong Chương 4; không có kết luận mạnh hơn số liệu.
