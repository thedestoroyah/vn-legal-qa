# Sprint 4 — Việc của Hùng (29/10 – 04/11/2026)

Tài liệu gồm các **thẻ việc**. Mỗi thẻ có đủ mục tiêu, file vào/ra, các bước và lệnh kiểm tra "xong chưa". Có thể dán nguyên một thẻ cho agent CLI hoặc web chat để nhờ hỗ trợ.

- Spec: `docs/superpowers/specs/2026-10-09-agentic-legal-qa-design.md`.
- Định dạng API: **Phụ lục A.5** trong `docs/managements/Đề cương DACNTT.md`.
- Phần Đạt làm song song (API, chạy thực nghiệm, bộ chấm): `docs/superpowers/plans/2026-10-28-sprint4-dat.md`.

## Đọc trước

Sprint 2 xong hết, cảm ơn Hùng. Đạt đã:
- Kiểm chéo 37 câu manual, đặt `checked_by = "Dat"`.
- Sửa đáp án mẫu M_032: Điều 60 BLLĐ 2019 là về đào tạo, không phải thương lượng tập thể.
- Nạp BLLĐ 2012 vào chỉ mục.
- Chạy thử tác tử: câu temporal năm 2019–2020 trích đúng BLLĐ 2012.

Sprint 3 còn dở **H9, H10, H11, H12**. Các thẻ này giữ nguyên trong `docs/sprints/2026-10-16-sprint3-hung.md`, trừ H10 đổi như thẻ H10' bên dưới. Ưu tiên làm H11 (thang chấm) trước H14, vì cần thang để chấm tay.

## Thứ tự và hạn

| Thẻ | Việc | Hạn | Phụ thuộc |
|---|---|---|---|
| H16 | Xem lại câu M_017 | 30/10 | — |
| H10' | Duyệt prompt chấm trong `eval/judge.py` | 31/10 | — |
| H11 | Thang chấm tay 3 mức (thẻ Sprint 3) | 31/10 | H10' |
| H9 | Từ chối, nhãn "chưa có căn cứ", trace dễ đọc (thẻ Sprint 3) | 01/11 | — |
| H13 | Ghép giao diện với API | 02/11 | H9; API của Đạt (Task 5) |
| H14 | Chấm tay 20 câu, tính mức đồng thuận | 03/11 | H11; phiếu chấm của Đạt (Task 6) |
| H12, H15 | Chương 2 (thẻ Sprint 3), Chương 1 | 04/11 | — |

Nghiệm thu Sprint 4 (04/11):
- Giao diện gọi API thật, kiểm cùng Đạt trên máy Đạt.
- Hai người đã chấm xong 20 câu, có tỷ lệ khớp với bộ chấm LLM.
- Có bản nháp Chương 1 và Chương 2.

## Quy trình chung

Giống Sprint 3:
- Luôn `git pull` trước khi làm. Commit nhỏ theo từng thẻ.
- **Không sửa** code của Đạt: `src/agent/`, `src/api/`, `src/generation/`, `src/retrieval/`, `src/ingestion/`, `eval/*.py`. Thấy lỗi thì báo Đạt.
- File của Hùng: `src/ui/`, `eval/manual_cases.json`, `docs/rubric.md`, `docs/judge_review.md`, phiếu chấm `eval/results/grading_rq3_hung.csv`, bản nháp báo cáo.

---

## H16 — Xem lại câu M_017

**Vấn đề:** câu M_017 hỏi "Vào tháng 6/2021, công ty muốn ký hợp đồng lao động mùa vụ 5 tháng với nhân viên thì có được phép không?". Đáp án mẫu là "Không được, vì BLLĐ 2019 đã bỏ loại HĐ mùa vụ". Tác tử lại trả lời "được ký HĐ xác định thời hạn dưới 12 tháng cho công việc mùa vụ" (BLLĐ 2019 Điều 18 Khoản 2).

BLLĐ 2019 bỏ **loại** HĐ mùa vụ, nhưng vẫn cho ký HĐ **xác định thời hạn** 5 tháng để làm việc mùa vụ. Vì vậy đáp án "không được" dễ bị phản biện.

**Các bước:**
1. Đọc lại Điều 18 và Điều 20 BLLĐ 2019: `python -m eval.show_article BLLD2019 20` và `python -m eval.show_article BLLD2019 18`.
2. Sửa M_017 trong `eval/manual_cases.json` theo một trong hai cách:
   - **Cách a, giữ ý định kiểm tra RQ4:** đổi câu hỏi thành "Vào tháng 6/2021, công ty có được ký **loại** hợp đồng lao động theo mùa vụ không, hay phải dùng loại hợp đồng nào?". Đáp án: "BLLĐ 2019 chỉ còn 2 loại HĐ (không xác định thời hạn và xác định thời hạn); việc mùa vụ ký HĐ xác định thời hạn."
   - **Cách b:** giữ câu hỏi, sửa đáp án thành "Được ký HĐ xác định thời hạn 5 tháng; BLLĐ 2019 không còn loại HĐ mùa vụ riêng", và thêm `BLLD2019_Dieu18_Khoan2` vào `gold_citations`.
3. Đặt `"checked_by": null` cho M_017 để Đạt kiểm lại.

**Xong khi:** `python -m eval.import_cases` chạy không lỗi, và báo Đạt đã đổi câu nào.

---

## H10' — Duyệt prompt chấm → `docs/judge_review.md`

**Thay cho H10 cũ.** Đạt đã viết prompt chấm ngay trong code (`JUDGE_RULES` trong `eval/judge.py`), vì bộ chấm cần chạy thử sớm. Việc của Hùng là **đọc và góp ý**, không viết lại.

**Các bước:**
1. Mở `eval/judge.py`, đọc `JUDGE_RULES`. Đây là định nghĩa và thang 0 / 0,5 / 1 của Faithfulness và Correctness, kèm 2 ví dụ.
2. So với định nghĩa RAGAS và với thang chấm tay (H11). Hai bên phải **dùng cùng định nghĩa**, nếu không thì so người với LLM là vô nghĩa.
3. Ghi vào `docs/judge_review.md`:
   - Chỗ nào định nghĩa mơ hồ, hoặc khác với thang chấm tay.
   - Gợi ý thêm hoặc sửa ví dụ (lấy ví dụ thật từ `python -m eval.show_article ...`).
   - Các trường hợp biên chưa có quy tắc (vd câu trả lời đúng nhưng trích sai Điều).

**Xong khi:** có `docs/judge_review.md`, và Đạt đã đọc. Đạt mới là người sửa `eval/judge.py`.

---

## H13 — Ghép giao diện với API

**Mục tiêu:** `src/ui/app.py` gọi API thật khi có biến môi trường `API_URL`, và vẫn dùng phản hồi mẫu khi không có. Nhờ vậy Hùng làm giao diện trên Windows mà không cần cài mô hình.

**API của Đạt** (`uvicorn src.api.main:app --port 8000`):
- `POST /api/ask`, gửi `{"question": "...", "config": "full"}`:
  - 200: trả JSON theo Phụ lục A.5.
  - 422: câu hỏi rỗng, dài quá 1000 ký tự, hoặc config sai. Thân lỗi có `detail` là danh sách lỗi.
  - 503: LLM quá tải. Thân lỗi có `detail` là câu thông báo tiếng Việt, hiển thị nguyên câu đó.
- `GET /api/article/{law_id}/{article}`, vd `/api/article/BLDS2015/357`:
  - 200: một Điều có `chunk_id`, `document`, `article`, `article_title`, `content`.
  - 404: không có Điều đó.
- `GET /health`: `{"status": "ok", "model": "..."}`.
- Mỗi câu hỏi mất khoảng **10–60 giây**, vì free tier phải giãn cách giữa các lượt gọi. Đặt timeout 180 giây.

**Các bước:**

1. Ở đầu `src/ui/app.py`, thêm `import os` và `import requests` (`requests` đã có sẵn theo `streamlit`). Thêm hằng:
   ```python
   API_URL = os.environ.get("API_URL", "").rstrip("/")  # trống: dùng phản hồi mẫu (làm UI không cần chạy mô hình)
   TIMEOUT = 180  # giây; tác tử free tier mất 10–60 s mỗi câu
   ```
2. Thay hàm `ask` và `get_article`:
   ```python
   class ApiError(Exception):
       """Lỗi gọi API, mang câu thông báo để hiển thị cho người dùng."""


   def ask(question):
       if not API_URL:
           return json.loads(SAMPLE.read_text(encoding="utf-8"))  # hoặc mẫu chọn ở thanh bên nếu đã làm H9
       try:
           r = requests.post(f"{API_URL}/api/ask", json={"question": question, "config": "full"}, timeout=TIMEOUT)
       except requests.RequestException:
           raise ApiError("Không kết nối được máy chủ hỏi đáp. Kiểm tra API đã chạy chưa.")
       if r.status_code == 422:
           raise ApiError("Câu hỏi không hợp lệ (rỗng hoặc dài quá 1000 ký tự).")
       if r.status_code != 200:
           raise ApiError(r.json().get("detail", f"Lỗi máy chủ ({r.status_code})."))
       return r.json()


   def get_article(chunk_id):
       if not API_URL:
           if not ARTICLES.exists():
               return None
           return json.loads(ARTICLES.read_text(encoding="utf-8")).get(article_key(chunk_id))
       law_id, number = article_key(chunk_id).split("_Dieu")
       try:
           r = requests.get(f"{API_URL}/api/article/{law_id}/{number}", timeout=30)
       except requests.RequestException:
           return None
       return r.json() if r.status_code == 200 else None
   ```
3. Ở chỗ gọi `ask` (khi người dùng nhập câu hỏi), thêm vòng quay chờ và hiển thị lỗi:
   ```python
   if question:
       with st.spinner("Đang tra cứu và soạn câu trả lời (có thể mất tới 1 phút)..."):
           try:
               st.session_state["history"].append((question, ask(question)))
           except ApiError as e:
               st.error(str(e))
               st.stop()
       st.rerun()
   ```
4. Cập nhật docstring đầu file: "Giao diện Streamlit: gọi API khi đặt API_URL, nếu không thì dùng phản hồi mẫu."

**Xong khi:**
- Trên máy Hùng, `streamlit run src/ui/app.py` (không đặt `API_URL`) vẫn chạy với phản hồi mẫu như trước.
- Trên máy Đạt, kiểm cùng nhau:
  1. Mở terminal 1, chạy `uvicorn src.api.main:app --port 8000`.
  2. Mở terminal 2, chạy `API_URL=http://localhost:8000 streamlit run src/ui/app.py`.
  3. Hỏi lần lượt 3 câu: một câu situational, một câu ngoài phạm vi, một câu "Điều 357 Bộ luật Dân sự 2015 quy định gì?". Cả 3 câu có câu trả lời thật, thẻ trích dẫn bấm mở được toàn văn Điều.
  4. Tắt API rồi hỏi tiếp: giao diện hiện "Không kết nối được máy chủ…", không hiện traceback đỏ.

---

## H14 — Chấm tay 20 câu và tính mức đồng thuận

**Mục tiêu:** kiểm định bộ chấm LLM (spec mục 7). Hai người chấm độc lập cùng 20 câu, sau đó so với điểm của LLM.

**Đầu vào:** Đạt tạo phiếu bằng lệnh `python -m eval.agent_eval sheet --rq rq3 --subset 60 --n 20` (Đạt tạo lại ngày 29/10 sau khi chạy lại với prompt route đã sửa; khoảng 21 câu, các câu Zalo không có đáp án mẫu nên chỉ chấm faithfulness) rồi commit file `eval/results/grading_rq3.csv`. File có các cột `id, question, answer, contexts, reference_answer, faithfulness, correctness, note`. Phiếu **không có** điểm của LLM, để người chấm không bị ảnh hưởng.

**Các bước:**
1. Chép `eval/results/grading_rq3.csv` thành `eval/results/grading_rq3_hung.csv`. Mở bằng Excel (file là UTF-8 có BOM nên tiếng Việt hiển thị đúng).
2. Chấm từng dòng theo thang ở `docs/rubric.md` (H11). Điền **0**, **0,5** hoặc **1** vào cột `faithfulness` và `correctness`.
   - Faithfulness: câu trả lời so với cột `contexts`.
   - Correctness: câu trả lời so với cột `reference_answer`.
   - `reference_answer` trống (câu Zalo) thì để trống ô `correctness`.
3. **Không xem phiếu của Đạt** và không xem `eval/results/agent_rq3_judge.jsonl` trước khi chấm xong.
4. Lưu lại ở định dạng CSV, giữ nguyên tên cột, rồi commit.
5. Đạt (hoặc Hùng, nếu đã cài đủ môi trường) chạy:
   ```
   python -m eval.agent_eval agree --rq rq3 --filled eval/results/grading_rq3_hung.csv
   python -m eval.agent_eval agree --rq rq3 --filled eval/results/grading_rq3_dat.csv
   ```
   Kết quả có dạng `faithfulness: khớp 0.850 trên 20 câu`.
6. Ghi vào `docs/rubric.md`, mục "Kết quả kiểm định":
   - Tỷ lệ khớp của từng người với LLM.
   - Tỷ lệ khớp giữa hai người. Đếm trong Excel bằng cách đặt 2 phiếu cạnh nhau, đếm số ô giống nhau chia cho số ô cùng có điểm.
   - 2–3 ví dụ cụ thể mà LLM chấm lệch.

**Xong khi:** có 2 phiếu đã điền và mục "Kết quả kiểm định" trong `docs/rubric.md`.

---

## H15 — Bản nháp Chương 1 (tổng quan đề tài)

**Mục tiêu:** khoảng 4–6 trang, viết trong file báo cáo chung theo mẫu khoa.

**Các mục:**
1. Đặt vấn đề: nhu cầu tra cứu pháp luật, khó khăn khi văn bản hết hiệu lực hoặc bị thay thế (ví dụ BLLĐ 2012 → 2019).
2. Mục tiêu đề tài và 4 câu hỏi nghiên cứu RQ1–RQ4. Chép từ mục 2 của spec, viết lại thành văn xuôi.
3. Phạm vi: 5 văn bản, không có Nghị định/Thông tư, văn bản gốc chưa hợp nhất. Lấy từ mục 3 và 10 của spec.
4. Đóng góp chính và bố cục báo cáo.

Yêu cầu trích dẫn giống H12: chỉ dùng tài liệu ở mục 12 của đề cương; tài liệu khác ghi `[CẦN KIỂM TRA]`.

**Xong khi:** gửi link bản nháp cho Đạt.
