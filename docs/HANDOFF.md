# Bàn giao phiên làm việc (cập nhật 11/11/2026)

> Nhật ký của Đạt, **track trong git từ 10/11** (trước đó bị gitignore). Bối cảnh ít đổi (đề tài, kiến trúc, quy tắc tập kiểm thử, lệnh): `AGENTS.md`. Claude Code tự nạp cả hai qua `IT_Project/CLAUDE.md` (thư mục cha, ngoài git), dù mở phiên ở `IT_Project/` hay `vn-legal-qa/`.
>
> Trước 10/11 file nằm ngoài git nên từng bị khôi phục về bản cũ (05/11, do rollback phiên). Từ 10/11 có lịch sử trong git: nếu ngày cập nhật ở trên cũ hơn `git log`, xem `git log -p -- docs/HANDOFF.md` trước khi tin file.
>
> **Quy tắc cập nhật (Đạt, 11/11):** khi Đạt yêu cầu cập nhật hoặc kiểm HANDOFF cho phiên mới: (1) rà lại **mọi mục cũ** (trạng thái, việc tiếp theo, prompt, kế hoạch) và sửa chỗ đã sai, không chỉ thêm mục mới ở cuối; (2) ghi **nhật ký của phiên** (commit, việc đã làm, số liệu, khó khăn và tình trạng, tiến độ PLAN) để làm báo cáo tuần; (3) đọc lại như một phiên mới chưa biết gì và kiểm đủ để làm tiếp.

## 1. Trạng thái

**Git:** phiên 10/11 có 8 commit tài liệu trên `main` (`dc951b0` → commit plan H22, xem mục 6) + 8 commit 10–11/11 (`43d4844` → commit HANDOFF cuối: vá lỗi giao diện, H23 ghép báo cáo, lỗi nhỏ sau review, HANDOFF) **chưa push**; không còn file sửa chưa commit, chỉ còn file chưa track (mục 8, "Trạng thái git"). Tag chỉ ở máy Đạt, chưa push: `ui-before-h22` (giao diện trước mọi sửa đổi), `h22-attempt` (bản H22 đầy đủ đã làm rồi bỏ: 12 commit, 353 test, review độc lập). Test: 371 pass. HANDOFF được track trong git từ 10/11.

**Sprint 5 (05/11–15/11):** phần của Đạt xong hết (Task 1–7, phân tích lỗi, latency, kiểm giao diện H19). Sổ quyết định: `.superpowers/sdd/2026-11-05-sprint5-dat/progress.md`. **10/11: Đạt làm thay H17, H18, H21** (Hùng không cập nhật gì từ 06/11); sổ quyết định `.superpowers/sdd/2026-11-05-sprint5-hung/progress.md`.

**Sprint 6 (16/11–27/11, làm sớm được vì không phải tính năng mới):** plan đã được Đạt duyệt: `docs/superpowers/plans/2026-11-16-sprint6-dat.md`; thẻ Hùng `docs/sprints/2026-11-16-sprint6-hung.md` (H22 giao diện, H23 ghép báo cáo, H24 slide bảo vệ, H25 video demo). Chạy 06/11 theo `superpowers:executing-plans`: **Task 1, 3, 4 xong, đã commit và push; Task 2 chạy được, chỉ còn Đạt mở giao diện bằng trình duyệt một lần.** Đã qua review độc lập cuối; các lỗi Important và Minor của Sprint 6 đã sửa (H22 mục 7 đã vá 11/11, mục 8 còn treo). Image `vn-legal-qa` 3,23 GB đã build trên máy Đạt. **H23 Đạt làm thay xong 11/11 (mục 7)**; Task 5 (rà soát, Turnitin) làm sau khi đổi khung báo cáo sang mẫu đúng (mục 8). Tiến độ và mọi quyết định: `.superpowers/sdd/2026-11-16-sprint6-dat/progress.md`.

**Báo cáo tuần 12:** xong, **không sửa nữa** (`docs/managements/Week 02.11-08.11/`: content.json, build_pptx.js, build_xlsx.py, 3 file; ngày báo cáo 06/11). Việc làm ngày 06/11 tính vào báo cáo tuần 13, xem mục 5. Mỗi giải pháp ở chương 4 và slide 10 ghi tình trạng: Đã xử lý / Giảm thiểu / Chấp nhận, ghi vào giới hạn / Đang theo dõi. `build_docx.py` có tùy chọn `ch4.resolved` (danh sách [nhãn, nội dung]) in dưới Bảng 4.1, dùng từ tuần 13 cho khó khăn tuần trước đã xong.

**Bảng số liệu dùng cho báo cáo** (`eval/results/`): `retrieval_rq1.md`, `retrieval_rq2.md`, `agent_rq3_ablation209.md` (5 cấu hình, 209 câu), `agent_rq3_heldout30.md`, `agent_rq4.md` (32 câu temporal), `agent_rq4_heldout20.md`, `agent_rq3_latency.md` (19 câu; `no_verify` n=18), `errors_rq3.md`, `verify_attack.md`, `v1_vs_v2.md`. Hình: `docs/report/figures/`. Ba bảng cũ còn số M_017 trước khi sửa đã xóa (còn trong git).

**Kết quả chính:**
- RQ1 (77 câu Zalo): hybrid+rerank Hit@5 0,844, Recall@10 0,872. RQ2: article 0,883/0,890 > clause_plain 0,857/0,872 ≈ clause_header 0,844/0,872 ≫ fixed 0,597/0,617.
- RQ3, 209 câu, so với full (* = khoảng tin cậy không chứa 0): no_router đúng phiên bản −0,250* (n=32), recall −0,034, correctness −0,042 (chưa ý nghĩa); baseline precision −0,060*, phiên bản −0,250*; no_verify recall +0,034*, precision −0,016*; no_grading không khác. → H1 được ủng hộ ở chỉ số đúng phiên bản. Verify là lớp phòng vệ: đổi recall lấy precision.
- Tập giữ riêng 30 câu: full P 0,978 / R 0,767 / phiên bản 0,700 / correctness 0,750; no_router kém cùng chiều (−0,143 / −0,133 / −0,200 / −0,083) nhưng chưa có ý nghĩa. full trả lời ít hơn no_router (0,767 vs 0,833).
- RQ4, 32 câu: current kém event −0,312* (recall, phiên bản); any kém −0,188 về phiên bản, sát ngưỡng [−0,375; 0,000]. → H2: event > current được ủng hộ, event > any chưa.
- Phép thử verify: bắt 46/47 mồi cùng ngữ cảnh, 50/50 mồi khác văn bản, 0 báo động nhầm.
- H14 (Đạt chấm 20 câu, `grading_rq3_dat.csv`): khớp faithfulness 0,950, correctness 0,917, nhưng bộ chấm cho 1 ở mọi câu nên kappa = 0. Báo cáo phải ghi: một người chấm, cũng là người làm hệ thống.

**Lịch sử thay đổi cần nêu trong báo cáo:** verify v1 gỡ nhầm 47/63 mã đúng → v2 thêm tiêu đề Điều vào prompt verify (gỡ 28, 21 đúng); router từ chối nhầm câu dân sự → sửa prompt. Prompt được chỉnh sau khi thấy lỗi trên tập kiểm thử; tập giữ riêng 30 câu soạn sau khi chốt prompt (commit `caa4f2f`) để giảm giới hạn này. M_017 do Hùng sửa câu hỏi ngày 03/11, đã chạy lại 5 cấu hình + 3 chính sách.

**Ghi chú 03/11:**
- Sửa `lookup_article` (câu tra cứu trực tiếp không nêu ngày sự việc trả đúng Điều được nêu, kể cả văn bản đã hết hiệu lực, vd M_066 BLLĐ 2012); **không chạy lại thực nghiệm**: số liệu Chương 4 là của code trước bản sửa (tới `d8c459e`), đã ghi trong 4.6. Không sửa prompt router (3/204 câu xếp nhầm ngoài phạm vi), ghi ở 4.7.
- Kiểm 4 kịch bản demo qua API và giao diện: đúng hết, kể cả M_066. Latency `no_verify` giữ n=18.
- Lỗi 503 là Google quá tải, không phải mạng thư viện (đã thử trên cả hai mạng).

## 2. Việc tiếp theo

**Ưu tiên phiên tới** (theo thứ tự):

1. **Hỏi Đạt về git** (mục 8, "Trạng thái git"): Đạt push 8 commit; commit thư mục `HƯỚNG DẪN BÁO CÁO/`, bỏ file zip trùng; không commit file `.~lock…#`.
2. **Sửa báo cáo tổng (báo cáo cuối kỳ, `docs/report/final_52300098_52300106.docx`), hạn nộp ELIT trước ngày công bố hội đồng 1 tuần, chậm nhất 04/12:**
   1. *Đổi khung sang mẫu đúng của khoa* (mục 8): hỏi Đạt 3 câu hỏi mở, viết plan ngắn để Đạt duyệt, sửa `build_report.py` + test, build lại. Prompt ở mục 4.
   2. *Đối chiếu quy định:* `HƯỚNG DẪN BÁO CÁO/2. Quy định và hướng dẫn/` (QĐ 2284 trình bày, hướng dẫn trình bày: lề, cỡ chữ, giãn dòng, đánh số trang, chú thích, tài liệu tham khảo) và sheet "Thông tin môn học_DỰ ÁN" mục "Các lưu ý về nội dung bài làm" + sheet "Rubric" (file Excel ở mục 8): sửa chỗ lệch ở khung hoặc ở nội dung chương.
   3. *Rà soát nội dung (Task 5 Sprint 6):* đọc toàn bộ 6 chương theo rubric, số liệu khớp `eval/results/`, tham chiếu chéo, chính tả; sửa ở file `.md` rồi `python docs/report/build_report.py`. Prompt ở mục 4.
   4. *Hình còn thiếu:* Hình 3.1–3.4 và activity (H26 của Hùng, hạn 20/11); Hùng im lặng thì Đạt tự vẽ hoặc bỏ hình và sửa câu dẫn. Build `--strict` phải hết cảnh báo.
   5. *Hoàn thiện bản nộp:* mở docx bằng Word/OnlyOffice, cập nhật trường (Ctrl+A, F9) cho mục lục và danh mục; kiểm số trang; ghi ngày và ký ở trang cảm ơn, cam đoan; xuất PDF; Turnitin (Đạt tự nộp).
   6. *Nộp:* file `52300098_52300106.zip` lên ELIT gồm báo cáo PDF, bản scan kế hoạch có chữ ký GVHD và các mục khác ghi trong sheet "Thông tin môn học_DỰ ÁN" (đọc đủ ô "Nội dung nộp bài"). Repo và `chroma_db.zip` nộp 03/12 (mục 3).
3. **Báo cáo tuần 13 (09.11–15.11, nộp khoảng 13/11):** nội dung = mục 5 (việc 06/11) + mục 6 "Nhật ký phiên 10/11" + **mục 9 "Nhật ký phiên 10/11 tối – 11/11"**. Prompt ở mục 4.
4. **Task 2 Sprint 6:** Đạt mở `docker compose up --build` một lần (phải `--build`: image trên máy đang chứa giao diện H22 đã hủy), thấy "Đã kết nối · gemini-3.1-flash-lite" thì đánh dấu Task 2 ở `PLAN.md` và Phụ lục B.
5. **Theo dõi Hùng** (im lặng từ 06/11): gửi tin nhắn bản 11/11 (H23 Đạt đã làm; Hùng còn H26, H24, H25). H26: 4 hình lưu đúng tên `assets/diagrams/bi_encoder.png`, `cross_encoder.png`, `naive_rag.png`, `agentic_rag.png`, bỏ Hình 3.5 khỏi `chuong3_draft.md` (hạn 20/11), sửa `activity.drawio` rồi Đạt thêm `<!-- Hình 4.8: assets/diagrams/activity.png -->` + chú thích vào Chương 4. Khoảng 20/11 vẫn im lặng thì Đạt nhận H24 (slide).
6. Còn treo, nhỏ: mục 8 thẻ H22 (gợi ý "đợi vài giây rồi bấm Thử lại" sai với lỗi 500, `src/ui/web/api/client.py`). Tùy chọn: gỡ skill Taste (`rm -rf IT_Project/.agents/skills/design-taste-frontend`), tắt số liệu ẩn danh của Impeccable (`IT_Project/.claude/skills/impeccable/scripts/impeccable telemetry off`).

## 3. Rủi ro và lỗi nhỏ còn hoãn

- **Quota:** Gemini 500 lượt/ngày/key, hay báo 503 "high demand" (dòng lỗi được chạy lại ở lần sau). Groq khoảng 100 lượt chấm/ngày/key. Quota Gemini hồi khoảng 14:20 giờ VN.
- **Bộ chấm dễ dãi**: faithfulness ≈ 1 ở mọi cấu hình, kappa = 0 → dùng như chỉ số phụ, dựa chính vào citation P/R và đúng phiên bản.
- **Cỡ mẫu**: router chỉ có ý nghĩa ở đúng phiên bản; cần khoảng 390–1050 câu để recall/correctness có ý nghĩa → báo cáo là xu hướng.
- **Lỗi nhỏ, đã xếp loại 03/11:**
  - *Sửa ở Sprint 6* (ảnh hưởng người dùng hoặc tái lập): đã đưa vào Task 1 và Task 3 của plan Sprint 6. Lỗi "413 bỏ qua lặng lẽ" đã loại: code in thông báo và câu đó được chấm lại ở lần sau.
  - *Ghi vào báo cáo, không sửa* (sửa thì số liệu đổi): reranker `max_length=512` cắt 56/1.693 Điều (đã ghi 4.7); `version_correct` tính cả văn bản khác lĩnh vực (đã ghi 4.6); prompt chấm thiếu ví dụ 0 điểm.
  - *Bỏ qua:* `_safe_date` nhận "any" từ LLM; `agree` crash với ô "x"; `judge_results` hết quota chưa có test; `_SPLIT_RE` tách câu sai sau "Đ."; `drop_citations` mất chữ thường chung ngoặc; `ID_RE` không nhận mã `fixed`; `lost_sentences` lệch chỉ số; `agent_smoke.md` bị ghi đè; BLDS Điều 688–689 gán sai Chương (Chương không dùng khi embedding); `get_article` trả None trên biến thể `fixed`; 4 lỗi review Sprint 5 (`parse_categories` nhãn trùng, `sheet --tag`, `answer_sha` không gồm đáp án mẫu, `plots._mean` nhóm rỗng).
- **Docker chưa kiểm:** nạp đủ chỉ mục trong container (đã thử 3 chunk), tải mô hình trên máy sạch, chạy trên Windows.
- **Bộ nộp:** `IT_Project/submission/chroma_db.zip` (73 MB, 4 chỉ mục, ngoài repo, đã kiểm giải nén và truy xuất thật) nộp kèm repo ngày 03/12. Nếu nạp lại chỉ mục thì phải tạo lại: `python -c "import shutil; shutil.make_archive('../submission/chroma_db', 'zip', root_dir='.', base_dir='chroma_db')"` khi không có container nào đang chạy.
- **Tài liệu tham khảo đã tra 03/11** (arXiv API, ACL Anthology, Crossref, NeurIPS, bản PDF của tác giả): 13 mục mục 12 đề cương + Lewis 2020. Sửa: BGE-M3 → tên mới + Findings ACL 2024, 2318–2335; Reuter thêm trang 17–30; RAGAS 'Espinosa Anke'; thêm DOI. BM25 giữ 3(4) 333–389 (trang nhà xuất bản/Crossref ghi 4(1-2) 1–174 là sai). CRAG chỉ có bản arXiv. Chương 1 hết `[CẦN KIỂM TRA]`. Danh mục đã chuyển sang APA 7 khi ghép docx (H23, `docs/report/tai_lieu_tham_khao.md`).

## 4. Gợi ý prompt cho phiên mới

**Tiếp tục chung**
```
Tóm tắt trạng thái hiện tại và 3 việc nên làm tiếp. Chưa làm gì, chưa commit.
```

**Chạy Task 5 Sprint 6 (sau khi đổi khung, mục 8)**
```
Chạy Task 5 của plan docs/superpowers/plans/2026-11-16-sprint6-dat.md (rà soát báo cáo), đọc ledger .superpowers/sdd/2026-11-16-sprint6-dat/progress.md trước. Báo cáo sinh bằng python docs/report/build_report.py: sửa lỗi ở file .md rồi build lại. Turnitin tôi tự nộp. Không commit, báo tôi khi xong.
```

**Pull việc của Hùng**
```
Repo có cập nhật, pull về (theo CLAUDE.md), kiểm tra Hùng sửa gì, chạy test, báo xung đột với AGENTS.md (nhất là tập kiểm thử, prompt) rồi làm tiếp.
```

**Báo cáo tuần mới**
```
Đọc docs/managements/tools/README.md và docs/HANDOFF.md mục 5, 6, 9. Làm báo cáo tuần 13 (09.11-15.11) trong docs/managements/Week 09.11-15.11: chép content.json, build_pptx.js, build_xlsx.py của tuần 12 rồi sửa; cùng 4 chương, cùng thiết kế. Tính cả việc làm ngày 06/11 ghi ở mục 5, thêm việc phát sinh từ 07/11 lấy từ git log (cả của Hùng). Khó khăn tuần 12 đã xong thì chuyển sang ch4.resolved, còn lại giữ nhãn tình trạng. Kiểm bằng ảnh render.
```

**Đổi khung báo cáo (phiên tới)**
```
Đọc HANDOFF mục 8. Đổi khung báo cáo sang TemplateCacMonDuAnVaThucTap_KhoaCNTT.dotx theo mục 8: hỏi tôi các câu hỏi mở trước, rồi viết plan ngắn (writing-plans) để tôi duyệt. Chưa commit.
```

**Commit việc mới**
```
Commit giúp tôi các thay đổi chưa commit thành vài commit hợp lý (quét key trong diff trước). Tôi sẽ tự push.
```

## 5. Ghi cho báo cáo tuần 13 (09.11–15.11)

Các việc dưới đây làm ngày **06/11** (cuối tuần 12) nhưng **không có trong báo cáo tuần 12**: Đạt quyết định không sửa báo cáo tuần 12, tính vào báo cáo tuần 13. Khi viết, ghi rõ ngày 06/11 và là làm sớm so với lịch (Sprint 6 bắt đầu 16/11). Đây là sửa lỗi và đóng gói, không phải tính năng mới, nên không trái mốc đóng băng 12/11. Số liệu dưới đây đã đo trong phiên 06/11; số trong báo cáo vẫn phải lấy từ nguồn ghi kèm.

**Đạt (commit `be47bd5..d5e4152`, tương ứng Sprint 6 Task 1–4):**
- Sửa lỗi ảnh hưởng người dùng và tái lập: chạy lại thực nghiệm không còn crash khi lần trước bị dừng giữa lúc ghi; điểm chấm JSON hỏng được chấm lại thay vì ghi rỗng; `/api/article` không phân biệt hoa thường; chỉ mục thiếu hoặc lệch báo rõ lệnh nạp lại và API trả 500 dạng JSON (Bảng 3.4). Bộ kiểm thử từ 319 lên 339 test, tất cả đạt.
- Đóng gói Docker: `Dockerfile`, `docker-compose.yml` với 2 dịch vụ `api` và `ui`. Image 3,23 GB; khi đã có sẵn mô hình, hệ thống lên trong khoảng 1 phút; API dùng khoảng 1,5 GB RAM. Cổng chỉ mở trên máy cục bộ. Đã chạy thử trên bản sao sạch như người chấm vừa clone. Task 2 còn bước Đạt mở giao diện bằng trình duyệt.
- Bộ nộp `chroma_db.zip`: 73 MB, đủ 4 chỉ mục (4.853 / 4.853 / 1.693 / 1.679 chunk), đã kiểm giải nén và truy xuất thật, giúp người chấm khỏi nạp lại khoảng 2 giờ CPU (ước tính từ 1,4 giây/chunk).
- Viết lại `README.md` theo 3 đối tượng: chạy thử, phát triển, tái lập thực nghiệm, có bảng "kết quả trong báo cáo ↔ lệnh ↔ file". Đã kiểm thật: 7 bảng kết quả, 4 hình và tập kiểm thử tái lập khớp từng byte từ dữ liệu đã lưu (không gọi LLM). Chưa chạy lại RQ1, RQ2 (mỗi cái khoảng 1 giờ CPU).
- Dọn mã: sửa lỗi lint, xóa `eval/validate_chunks.py` và 3 file `test.txt` rỗng.
- Review độc lập cuối: 0 Critical, 2 Important; đã xử lý hết, trừ 2 mục giao diện chuyển cho Hùng (H22 mục 7–8).
- Đồng bộ tài liệu: `PLAN.md`, Phụ lục B đề cương, spec mục 6, Bảng 3.4 Chương 3, thẻ H22 và H25.

**Hùng:** bản nháp Chương 2 (H12, commit `bf00174` ngày 06/11) và cập nhật khung báo cáo `final_52300098_52300106.docx`. Báo cáo tuần 12 còn ghi Chương 2 là việc của tuần 13, nên tính vào đây là đúng.

**Tiến độ:** đếm trong `docs/PLAN.md`: 66/76 hạng mục sau 06/11, trước đó 62/76. Báo cáo tuần 12 ghi 62/74, mẫu số lệch 2 chưa rõ lý do: đếm lại và thống nhất cách đếm khi viết.

**Phát hiện đưa vào phần khó khăn:**
- Giao diện chạy venv mà chưa bật API thì tự chuyển sang dữ liệu dự phòng (chỉ BM25) nhưng vẫn hiện "Đã kết nối". Tình trạng: đã xử lý 10/11 (thanh bên ghi "Dự phòng: chỉ BM25"); Docker tắt hẳn dự phòng (`UI_LOCAL_FALLBACK=0`).
- Lần đầu tải mô hình tới khoảng 7 GB (kế hoạch dự tính 4,5 GB) và nạp chỉ mục khoảng 2 giờ. Tình trạng: đã xử lý bằng `chroma_db.zip`, README ghi đúng dung lượng.
- Docker chưa kiểm trên Windows và chưa thử tải mô hình trên máy sạch. Tình trạng: đang theo dõi, nhờ Hùng thử.

**Kế hoạch phần còn lại trong báo cáo** (cập nhật 11/11; bản 06/11 ghi Hùng còn H17–H25 nay đã cũ): Đạt: đổi khung báo cáo sang mẫu đúng, Task 5 (rà soát, Turnitin), Task 2 (mở Docker); Hùng: H26 (hình Chương 3, activity), H24 (slide), H25 (video). H17, H18, H21, H23 Đạt đã làm thay; H22 đã hủy.

## 6. Phiên 10/11 (Đạt + Claude), đã commit

**Báo cáo thành 6 chương** (Đạt duyệt): thêm Chương 2 "Tổng quan tài liệu" (`docs/report/chuong2_draft.md`, mở rộng mục 7 đề cương, có Bảng 2.1 so sánh công trình và Bảng 2.2 vấn đề → giải pháp → RQ). File chương cũ đổi tên: `chuong2→3` (lý thuyết, Hùng), `3→4` (thiết kế), `4→5` (thực nghiệm), Chương 5 mới viết → `chuong6_draft.md`. Mọi tham chiếu "Chương/mục/Bảng/Hình" trong 6 chương, README, thẻ H23–H24, Task 5 plan Sprint 6 đã dời; mục cũ trong PLAN/Phụ lục B giữ số cũ (có dòng ghi chú). Đã kiểm bằng script: không còn tham chiếu trỏ tới mục/bảng/hình không tồn tại.
- Tài liệu mới: ALQAC 2025 (Do và cộng sự, KSE 2025, DOI 10.1109/KSE68178.2025.11309650) thêm vào mục 12 đề cương.
- **Mục 7 đề cương mô tả sai Nguyen Ba 2024**: bài gốc (arXiv 2409.13699, đã đọc toàn văn) xếp hạng lại bằng câu trả lời của LLM (Active Retrieval), không phải cross-encoder trước khi sinh, và có so sánh từng thành phần truy xuất. Chương 2 viết theo bài gốc; mục 7 đề cương đã sửa (commit `26ebbf0`).
- Pham 2025: đã đọc toàn văn (scitepress.org/Papers/2025/137354/137354.pdf): đo Legal Citation Accuracy theo nghĩa đúng chuẩn trình bày, loại quy định đã bị thay thế, không có đánh giá lược bỏ; Chương 2 viết theo đó.
- Chương 1 1.1.3 hạ mức khẳng định cho khớp nguồn.
**H17** Chương 1: 209 câu, tập giữ riêng, NiceGUI, kiểm định bộ chấm 1 người, lịch theo mục 11 đề cương.
**H21** Chương 6 (kết luận): Bảng 6.1 chỉ tiêu, trả lời RQ1–RQ4, 7 hạn chế ↔ 7 hướng phát triển; mọi số có trong Chương 5.
**DRM@5** thêm vào Bảng 5.3 (đã đo sẵn trong `retrieval_rq2.md`): Khoản + tiêu đề 0,075 thấp nhất (Khoản chỉ nội dung 0,101); có định nghĩa ở 5.1.2 và 1 câu ở Chương 6.
**H18** `assets/diagrams/usecase.drawio/.png`, `sequence.drawio/.png` (PNG rộng 2755/3255 px), đã điền vào Hình 4.6–4.7. Sửa tiếp bằng drawio. **Xuất PNG từ terminal VSCode phải bỏ biến** `ELECTRON_RUN_AS_NODE`: `env -u ELECTRON_RUN_AS_NODE drawio -x -f png -s 2 -b 10 -o X.png X.drawio` (không bỏ thì Electron chạy như Node và báo lỗi `BrowserWindow`).
**Hình 4.1, 4.2 vẽ lại (10/11)** bằng draw.io theo code: `assets/diagrams/architecture.drawio/.png`, `agent_graph.drawio/.png`; phong cách giống ảnh cũ (banner, khối tầng có dải tiêu đề, icon Breeze của KDE có sẵn trên máy, LGPL, đổi màu và làm nét dày). Ảnh cũ của Hùng (AI vẽ, sai: Streamlit, thiếu Verify, nhánh Direct không tồn tại) giữ lại là `architecture_old.png`, `agent_graph_old.png`, không dùng. Giao Hùng **H26** (thẻ Sprint 6): sửa 7 điểm của `activity.drawio`, vẽ Hình 3.1–3.4, bỏ Hình 3.5. Script sinh sơ đồ nằm ở scratchpad (sẽ mất); sửa tiếp thẳng trên file `.drawio`.
**Khung docx của Hùng** (`final_52300098_52300106.docx`, 5 chương): 11/11 đổi tên thành `khung_TDTU.docx` và dùng làm khung cho script ghép báo cáo (mục 7); tên cũ giờ là file sinh ra.
**Lỗi nhỏ của review:** đã sửa hết theo yêu cầu của Đạt (10/11): nhánh dự phòng trong sơ đồ tuần tự, RRF/số ứng viên ở Chương 3, "triệt tiêu DRM", tên Chương 3–5 theo khung docx, nhãn câu tổng hợp ở Bảng 5.1. Trường `checked_by` của 65 câu tổng hợp vẫn trống (chỉ là metadata, không sửa tập kiểm thử).

**Review độc lập cuối (10/11):** 4 Critical + 8 Important đã sửa hết; chi tiết và các lỗi nhỏ hoãn ở `.superpowers/sdd/2026-11-05-sprint5-hung/progress.md` (dòng `Final:`). Sửa cả 2 lỗi có từ trước trong Chương 5 (bản cũ của Đạt): câu "bỏ grade giảm độ trễ nhiều nhất" (thực ra là dao động API) và "Cit. P của `any` thấp hơn rõ" (ghép cặp không có ý nghĩa). Pham 2025 có toàn văn: scitepress.org/Papers/2025/137354/137354.pdf. Mục 7 đề cương đã sửa 2 chỗ (Nguyen Ba, Answer Correctness của RAGAS).
**Commit:** các file chương phải vào **cùng một commit** (git thấy `chuong2/3/4` là viết lại, không phải đổi tên). Báo Hùng pull trước khi sửa `docs/report/`.

### Nhật ký phiên 10/11 (dùng cho báo cáo tuần 13)

Hùng không cập nhật gì từ 06/11 nên Đạt làm thay các thẻ đang chặn việc ghép báo cáo. Tất cả là tài liệu, sơ đồ và plan; không sửa code, test giữ 339 pass.

**Commit (theo thứ tự):** `dc951b0` bìa báo cáo tuần 12 (bản đã nộp) · `c73ee89` sơ đồ use case, sequence (H18) · `d53515f` báo cáo 6 chương · `26ebbf0` mục 7 đề cương, ALQAC, PLAN, thẻ · `b578dad` HANDOFF vào git · `267d9f1` vẽ lại Hình 4.1, 4.2 · `751d0f9` thẻ H26 · commit plan H22.

**Báo cáo:**
- H17 cập nhật Chương 1 (209 câu, tập giữ riêng 30 câu, NiceGUI, kiểm định bộ chấm một người, lịch theo đề cương).
- Thêm **Chương 2 "Tổng quan tài liệu"** (Đạt duyệt): báo cáo thành 6 chương, dời số và sửa mọi tham chiếu chéo (kiểm bằng script). Đọc lại toàn văn 2 công trình trong nước (Nguyen Ba 2024, Pham 2025), thêm tài liệu ALQAC 2025, sửa 2 mô tả sai ở mục 7 đề cương.
- H21 viết Chương 6 (kết luận, 7 hạn chế ↔ 7 hướng phát triển); thêm cột DRM@5 vào Bảng 5.3.
- Review độc lập cuối: 4 Critical + 8 Important, sửa hết, gồm 2 lỗi có từ trước ở Chương 5 (câu về độ trễ của bước grade, câu về Citation Precision của chính sách `any`); các lỗi nhỏ cũng đã sửa; Chương 3 bớt trùng với Chương 2.

**Sơ đồ:**
- H18: use case, sequence (draw.io, theo code).
- Kiểm `assets/diagrams/`: 2 ảnh do AI vẽ (Hùng) sai so với code (giao diện ghi Streamlit, thiếu bước Verify, có nhánh "Direct" không tồn tại) → vẽ lại Hình 4.1, 4.2 bằng draw.io, giữ phong cách cũ, ảnh cũ giữ là `*_old.png`. Sơ đồ activity lệch code 7 điểm, Chương 3 thiếu 5 hình → giao Hùng thẻ H26.

**Giao diện (H22, Đạt nhận thay Hùng):**
- Cài skill Impeccable (dùng được) và Taste (không hợp NiceGUI).
- Đánh giá theo quy trình 2 lượt độc lập: 20/40 điểm Nielsen; bộ phát hiện báo 29–40 cảnh báo (khoảng 20 chỗ chữ 10px, tương phản 2,2–2,6:1, ô icon kiểu mẫu chatbot). Lỗi thật phát hiện được: giao diện báo "Đã kết nối" khi đang chạy dự phòng; trang chủ ghi cứng "2.275 điều · 5.427 khoản" trong khi kho là 1.693 Điều, 4.853 Khoản.
- Viết plan H22 7 task (Đạt duyệt). Tạo tag rollback `ui-before-h22` và bản chép `IT_Project/backup/ui-before-h22/`.
- Tối 10/11: chạy hết 7 task (skill Impeccable; bộ phát hiện từ 29–40 xuống 2–4 cảnh báo; 353 test; review độc lập Opus 0 Critical) và kiểm Docker. Đạt xem rồi **quyết định hủy H22**, giữ giao diện cũ: chưa ấn tượng hơn bao nhiêu, mốc đóng băng 12/11, hội đồng chấm phần nghiên cứu. Đã lùi 12 commit (bản đầy đủ ở tag `h22-attempt`), chỉ giữ bản vá Task 1: số Điều/Khoản thật trên trang chủ, nhãn "Dự phòng: chỉ BM25", bỏ "chính xác", "chống bịa đặt" và lệnh `uvicorn` khỏi thông báo lỗi (README thay vào). Chụp lại ảnh trang chủ (`nicegui_01_home.png`, API thật); Hình 4.3–4.5 không đổi vì không chứa số sai.
- Có làm thử mockup thiết kế lại hoàn toàn (hướng "tờ lịch": ngày sự việc và biểu đồ hiệu lực là trung tâm, đối chiếu kết quả RQ4 event/current) rồi xóa theo ý Đạt. Ý tưởng đáng giữ cho slide H24: cặp câu trả lời thật của M_016 trong `eval/results/agent_rq4.jsonl` (event trích BLLĐ 2012 Điều 22, current trích BLLĐ 2019 Điều 20 là văn bản chưa có hiệu lực năm 2020).

**Tiến độ:** `PLAN.md` có 72 hạng mục xong / 80 (không tính 4 hạng mục đã hủy); sau 06/11 là 66/76. Mẫu số tăng vì thêm hạng mục mới (Chương 2, vẽ lại Hình 4.1–4.2, H26). Đếm lại khi viết báo cáo: `[x]` chia cho `[x]` + `[ ]` không gạch ngang.

**Khó khăn và tình trạng (cho chương 4 báo cáo tuần):**
- Hùng không phản hồi từ 06/11 → Đạt làm thay H17, H18, H21, H22; việc dồn vào H23 (24/11). *Đang theo dõi.*
- Ảnh sơ đồ do AI vẽ sai nội dung so với hệ thống → vẽ lại từ code bằng draw.io. *Đã xử lý* (Hình 4.1–4.2); H26 *đang chờ Hùng*.
- Giao diện hiển thị trạng thái và số liệu sai, trông như mẫu chatbot AI → đánh giá có điểm số, plan H22, làm thử rồi hủy; chỉ vá phần sai sự thật. *Đã xử lý* (số liệu, nhãn dự phòng); diện mạo: *chấp nhận, giữ giao diện cũ*.
- Đề cương mô tả sai một công trình liên quan so với bài gốc → đọc toàn văn, sửa đề cương và Chương 2. *Đã xử lý.*
- Máy không có Chrome nên bộ phát hiện không quét được trang → dùng Electron có sẵn qua cổng gỡ lỗi (CDP). *Đã xử lý.*

### Công cụ (cho phiên H22 và về sau)

- `IT_Project/tools/` (ngoài git): `ui_shot.js` chụp giao diện bằng Electron: `env -u ELECTRON_RUN_AS_NODE electron44 ../tools/ui_shot.js http://127.0.0.1:8080/ OUT.png 1440 900 "ask:<câu hỏi>" "click:<chữ đầu của phần tử>" "wait:<ms>"` (bước ask gõ bằng `insertText` + phím Enter; nút có icon thì chữ bắt đầu bằng tên icon, vd `menu_book`). `styled.py` + `icons.py` sinh Hình 4.1–4.2, `make_diagrams.py` sinh use case/sequence; từ giờ sửa thẳng file `.drawio`.
- Chạy giao diện không tốn quota (phát lại kết quả đã chạy): `LLM_API_KEY= UI_LOCAL_FALLBACK=1 API_URL=http://127.0.0.1:8999 .venv/bin/python -m src.ui.web.main`; tắt: `pkill -f '[s]rc\.ui\.web\.main'`. Câu hỏi đầu tiên chậm vì phải dựng chỉ mục BM25.
- Bộ phát hiện Impeccable không đọc file `.py`. Quét trang đang chạy: mở trang bằng Electron với `--remote-debugging-port=9333` (127.0.0.1), rồi `../.claude/skills/impeccable/scripts/impeccable detect --cdp 9333 --target 127.0.0.1:8080 --json` (cwd `vn-legal-qa`). Không dùng `live-server`/`live-inject` (sửa file của dự án).
- Hook của Impeccable (`IT_Project/.claude/settings.local.json`) chạy sau mỗi lần sửa file và khi kết thúc lượt, trong phiên mở ở `IT_Project/`.
- Mọi lệnh `drawio`/`electron44` từ terminal VSCode phải chạy với `env -u ELECTRON_RUN_AS_NODE`.

## 7. H23 ghép báo cáo (Đạt làm thay, 10–11/11), đã commit

Đạt quyết định không chờ Hùng (im lặng từ 06/11), chạy plan `docs/superpowers/plans/2026-11-10-h23-report-dat.md` (native, 5 task). Sổ quyết định: `.superpowers/sdd/2026-11-10-h23-report-dat/progress.md`.

**Cách làm:** script `docs/report/build_report.py` (thư viện chuẩn + `pandoc`, không thêm dependency): tiền xử lý 6 chương (bỏ ghi chú nháp, comment nguồn, số tiêu đề gõ tay; comment hình thành ảnh) → pandoc với khung làm reference → đổi style sang style khung (`Nidungvnbn`, `Caption`, `TableGrid`, `Bibliography`) → ghép vào `docs/report/khung_TDTU.docx`. Lệnh: `python docs/report/build_report.py` (`--strict` thoát mã 1 nếu còn cảnh báo). Kết quả `docs/report/final_52300098_52300106.docx`, khoảng 75 trang. 29 test trong `tests/test_build_report.py`. Ảnh: rộng tối đa 15 cm, giữ ≥ 150 dpi, cao ≤ 20 cm. Mục lục và hai danh mục trong file là dòng nhắc "Chưa cập nhật… F9" cho tới khi cập nhật trường.

**Theo `docs/managements/Template_VN.dotx`** (Đạt đưa 10/11, đã commit; 11/11 Đạt báo đây là mẫu cũ/mẫu môn học, mẫu đúng ở mục 8): chú thích "Hình 4.1: …"/"Bảng 5.1: …" có trường `STYLEREF 1 \s` + `SEQ Hình \s 1` (danh mục hình, bảng tự cập nhật); bảng có chú thích ở trên, hình ở dưới; tài liệu tham khảo APA 7, thụt treo 0,5", tên nguồn in nghiêng.

**Sửa so với khung của Hùng:** danh mục hình/bảng luôn rỗng (chú thích dùng mã "Hình_2." thay vì "Hình"); tài liệu tham khảo kiểu IEEE [1]… trong khi thân bài trích tác giả–năm → thay bằng 15 mục mục 12 đề cương (APA 7, có kiểm tự động trích dẫn ↔ danh mục); tiêu đề tiếng Anh khác đề cương → đúng nguyên văn mục 1; Tóm tắt, Abstract còn chữ mẫu → viết mới khoảng 200 từ mỗi bản từ số liệu Chương 6 (`docs/report/phan_dau.md`); bảng viết tắt trống → 20 từ có thật trong 6 chương; lời cảm ơn lặp chữ; cam đoan đổi "tôi" thành "chúng tôi" (Đạt quyết định). Chương mới sang trang, bảng rộng hết trang.

**Nguồn Markdown đã sửa:** Chương 4 tách chú thích gộp "Hình 4.3–4.5", "Hình 4.6–4.7" thành từng hình; Chương 3 bỏ nhãn `[CẦN KIỂM TRA]` cạnh Lewis (2020) (tài liệu đã có ở mục 12).

**Review độc lập (Opus):** 0 Critical, 3 Important, đã sửa có test: Hình 4.7 quá nhỏ, mục lục lưu sẵn của khung cũ, id ảnh pandoc không được đánh lại (sẽ trùng khi H26 thêm hình), tiêu đề cấp 4 Chương 3 lặp số. Không đưa `activity.png` vào báo cáo vì đang lệch code 7 điểm (H26). 10 lỗi nhỏ đã sửa nốt theo yêu cầu của Đạt (11/11): thứ tự APA, bảng viết tắt thêm AI/ALCE/JSONL, danh sách ngay sau dòng đoạn văn (Chương 3), numbering không trùng giữa các phần, kiểu file ảnh mới, vị trí updateFields, bỏ ~950 KB ảnh cũ, cột bảng theo nội dung + chữ bảng 11pt (style `BangNoiDung`), tài liệu tham khảo dòng đôi như mẫu khoa. Báo cáo khoảng 71 trang.

**Còn lại:** 5 cảnh báo "thiếu ảnh" Hình 3.1–3.5 (chờ H26; hiện ô "[CHỜ HÌNH 3.x: …]" trong file); mở bằng Word/OnlyOffice cập nhật trường; trang ký (ngày, chữ ký) làm tay ở bản nộp.

**Khó khăn (cho chương 4 báo cáo tuần 13):** Hùng không phản hồi, H23 hạn 24/11 chặn rà soát và Turnitin → Đạt làm bằng script, Markdown là nguồn duy nhất, build lại trong vài giây. *Đã xử lý.* Khung docx có lỗi định dạng ẩn (danh mục hình rỗng, kiểu trích dẫn lệch) → phát hiện khi đối chiếu với mẫu khoa. *Đã xử lý.*

## 8. Đổi khung báo cáo sang mẫu đúng (Đạt báo 11/11, chưa làm)

Khung đang dùng (`docs/report/khung_TDTU.docx`, do Hùng lấy từ mẫu mấy năm trước) và `docs/managements/Template_VN.dotx` (mẫu báo cáo môn học, nội dung ví dụ môn NLP) đều **sai mẫu**. Mẫu đúng: `docs/managements/HƯỚNG DẪN BÁO CÁO/3. Template báo cáo/DỰ ÁN CNTT/TemplateCacMonDuAnVaThucTap_KhoaCNTT.dotx`. Đạt nói: chỉ khác ở các trang đầu, từ Tóm tắt trở xuống giữ nguyên được.

**Trạng thái git (11/11, cuối phiên):** 8 commit chưa push: `43d4844` vá giao diện · `ccc6f78` nguồn Chương 3, 4 · `69a384f` script build · `3e70871` phần đầu, tài liệu, docx · `4e4c66e` tài liệu · `e3b2d47` lỗi nhỏ sau review · `e5c27c0` viết tắt, thứ tự APA, docx build lại · commit HANDOFF cuối (HANDOFF, AGENTS). Không còn file sửa chưa commit (371 test pass). Không commit `docs/managements/.~lock.Template_VN.dotx#` (file khóa của OnlyOffice). Chưa track: thư mục `docs/managements/HƯỚNG DẪN BÁO CÁO/` (Đạt thêm 11/11, có mẫu đúng, quy định trình bày, file Excel) và file `HƯỚNG DẪN BÁO CÁO-20261110T174410Z-1-001.zip` (bản nén trùng nội dung): hỏi Đạt commit thư mục (khung mới cần mẫu trong repo để build lại được) và bỏ file zip.

**Khác biệt đã đọc (11/11, chưa đọc hết):**
- Bìa chính và bìa phụ: "HỌ VÀ TÊN SINH VIÊN 1 – MSSV", "… 2 – MSSV" đứng **trước** "TÊN ĐỀ TÀI"; sau tên đề tài là "DỰ ÁN CÔNG NGHỆ THÔNG TIN" rồi "TÊN CHUYÊN NGÀNH"; bìa phụ thêm "Người hướng dẫn / TS. Nguyễn Văn A". Khung cũ để tên đề tài trước, "Người thực hiện" ở dưới.
- Mẫu đúng **không có** trang "PHẦN XÁC NHẬN VÀ ĐÁNH GIÁ CỦA GIẢNG VIÊN" (khung cũ có): sau cam đoan là "TÊN ĐỀ TÀI / TÓM TẮT".
- Lời cảm ơn, cam đoan: câu chữ như khung cũ (cam đoan xưng "tôi"; Đạt đã chọn "chúng tôi").
- **Lề trang khác trên toàn văn bản**, không chỉ trang đầu: mẫu đúng `top 1985, right 1134, bottom 1701, left 1985` twip (3,5 / 2 / 3 / 3,5 cm); khung cũ `1134 / 1134 (có section 851) / 1134 / 1701` (2 / 2 / 2 / 3 cm). Vùng chữ mẫu đúng rộng 15,5 cm (script đang giả định ảnh, bảng rộng tối đa 15 cm: vẫn vừa). Cần đối chiếu `HƯỚNG DẪN BÁO CÁO/2. Quy định và hướng dẫn/QĐ.2284.2020_Trình bày khóa luận.pdf` và `Huong dan trinh bay khoa luan TN, do an TN.docx` trước khi chọn lề.
- Cùng đánh số tiêu đề "CHƯƠNG %1.", cùng 5 section, 3 header. Chưa so: style thân bài (`Nidungvnbn`?), style chú thích, định dạng chú thích hình/bảng, kiểu tài liệu tham khảo, trang Tóm tắt/Abstract (ô mẫu có còn chữ "(Time New Romans – 13)" và tiêu đề tiếng Anh "TITLE" không) → script `fill_front_matter` tìm đoạn theo các chữ mẫu đó, phải sửa theo mẫu mới.

**Sheet "Thông tin môn học_DỰ ÁN"** (`HƯỚNG DẪN BÁO CÁO/Copy of QL. DỰ ÁN CNTT_ĐATN _KLTN.xlsx`; đọc bằng zipfile + sharedStrings, máy chưa có openpyxl trong .venv; các ô dài mới đọc 150 ký tự đầu, phiên sau đọc đủ): môn Dự án CNTT (504091), 3 tín chỉ, nhóm tối đa 2 SV; ngôn ngữ Tiếng Việt/Tiếng Anh; giữa kỳ (sau 8 tuần) chiếm 40% điểm; **nộp ELIT file `MSSV1_MSSV2.zip`** gồm báo cáo pdf, file scan kế hoạch có chữ ký GVHD, … (đọc đủ), trước 1 tuần so với ngày công bố hội đồng phản biện; khoa kiểm tra đạo văn và thể thức trình bày; 2 GV phản biện/đề tài, báo cáo trực tiếp, mang quyển báo cáo; mục "Các lưu ý về nội dung bài làm" (xác định vấn đề, ý nghĩa khoa học và thực tiễn, …) cần đọc đủ để đối chiếu Chương 1. Sheet "Rubric" chưa đọc (tiêu chí chấm, nên đọc trước khi rà soát Task 5).

**Câu hỏi mở cho Đạt:** tên chuyên ngành ghi trên bìa (vd "KHOA HỌC MÁY TÍNH"?); bỏ hẳn trang xác nhận GV hay giữ; lề theo mẫu mới hay theo QĐ 2284.

**Hướng làm đề xuất (cần plan + Đạt duyệt):** tạo khung mới từ mẫu đúng: phần từ đầu tới trước "TÓM TẮT" lấy của mẫu mới (điền tên, MSSV, tên đề tài nguyên văn đề cương mục 1, chuyên ngành, GVHD PGS.TS. Lê Anh Cường, năm 2026, lời cảm ơn, cam đoan "chúng tôi"), phần từ Tóm tắt trở xuống giữ của `khung_TDTU.docx` (để `build_report.py` khỏi đổi nhiều), lề trang mọi section theo mẫu mới; hoặc dùng thẳng mẫu mới làm khung nếu style thân bài trùng tên. Sửa `fill_front_matter` theo chữ mẫu mới, cập nhật test `test_front_matter_filled`, build lại, render kiểm (topdf.sh). Sửa thẻ H23, AGENTS.md (đã trỏ mẫu đúng), mục 7.

## 9. Nhật ký phiên 10/11 tối – 11/11 (Đạt + Claude), dùng cho báo cáo tuần 13

Ba việc lớn: chạy H22 rồi hủy (giữ giao diện cũ, chỉ vá lỗi sai sự thật); H23 ghép báo cáo bằng script (Đạt làm thay Hùng); phát hiện khung báo cáo dùng sai mẫu của khoa. Không sửa tác tử, API, prompt, tập kiểm thử: số liệu thực nghiệm không đổi.

**Commit (chưa push):** `43d4844` vá lỗi giao diện (số Điều/Khoản thật, nhãn "Dự phòng: chỉ BM25") · `ccc6f78` dọn nguồn Chương 3, 4 · `69a384f` script `build_report.py` + test, khung đổi tên `khung_TDTU.docx` · `3e70871` Tóm tắt, Abstract, viết tắt, tài liệu tham khảo APA, docx đã build · `4e4c66e` tài liệu (PLAN, Phụ lục B, thẻ Hùng, AGENTS, HANDOFF). Thêm `e3b2d47` lỗi nhỏ sau review · `e5c27c0` viết tắt, thứ tự APA, docx build lại · commit HANDOFF cuối (nhật ký phiên, việc đổi khung), AGENTS (trỏ mẫu báo cáo đúng).

**Việc đã làm:**
- **H22 giao diện:** chạy hết plan 7 task bằng skill Impeccable (bộ phát hiện 29–40 cảnh báo → 2–4; review độc lập 0 Critical); kiểm Docker thật (2 container, API healthy, câu hỏi thật đúng); làm thử 1 mockup thiết kế lại hoàn toàn. Đạt xem rồi **hủy H22**: chưa ấn tượng hơn bao nhiêu, mốc đóng băng 12/11, hội đồng chấm phần nghiên cứu. Lùi 12 commit (giữ ở tag `h22-attempt`), chỉ giữ bản vá 2 lỗi sai sự thật; chụp lại ảnh trang chủ bằng API thật.
- **Cân nhắc làm web riêng thay NiceGUI:** không làm (trái mốc đóng băng, không thêm số liệu, kéo theo sửa Chương 4, Docker, test).
- **H23 ghép báo cáo (Đạt làm thay):** viết `docs/report/build_report.py` (pandoc + thư viện chuẩn): 6 chương Markdown → `docs/report/final_52300098_52300106.docx` (71 trang) trong vài giây; Markdown là nguồn duy nhất. Sửa 4 lỗi có sẵn của khung Hùng: danh mục hình/bảng luôn rỗng (mã SEQ sai), tài liệu tham khảo IEEE lệch kiểu trích tác giả–năm, tiêu đề tiếng Anh khác đề cương, Tóm tắt/Abstract còn chữ mẫu. Viết Tóm tắt, Abstract (số liệu lấy từ Chương 6), danh mục 23 từ viết tắt, 15 tài liệu APA 7 có kiểm tự động trích dẫn ↔ danh mục.
- **Review độc lập H23 (Opus):** 0 Critical, 3 Important (sơ đồ tuần tự quá nhỏ, mục lục lưu sẵn của khung cũ, id ảnh có thể trùng gây hỏng file Word) + 1 lỗi tiêu đề lặp số → sửa có test; 10 lỗi nhỏ sửa nốt (thứ tự APA, viết tắt, danh sách trong Chương 3, chữ bảng 11pt, bỏ 950 KB ảnh thừa…).
- **Phát hiện sai mẫu báo cáo (cuối phiên):** khung Hùng và `Template_VN.dotx` là mẫu cũ; mẫu đúng `TemplateCacMonDuAnVaThucTap_KhoaCNTT.dotx` khác ở bìa, không có trang xác nhận GV, và **khác lề trang toàn văn bản**. Đã đọc sheet "Thông tin môn học_DỰ ÁN" (cách nộp ELIT `MSSV1_MSSV2.zip`). Chưa sửa, xem mục 8.

**Số liệu:** test 339 → 371 (thêm 29 test cho script báo cáo, 3 test giao diện); báo cáo docx 71 trang, 5 cảnh báo còn lại là Hình 3.1–3.5 chờ H26.

**Tiến độ `PLAN.md`:** 72 xong / 79 (không tính 5 hạng mục đã hủy, gồm H22) = 91%. H23 còn `[ ]` (chờ hình H26, đổi khung, cập nhật mục lục).

**Khó khăn và tình trạng (cho chương 4 báo cáo tuần):**
- Hùng không phản hồi từ 06/11 → Đạt làm thay H23 bằng script, nhắn Hùng còn H24, H25, H26. *Đang theo dõi.*
- Sửa giao diện tốn công nhưng hiệu quả nhìn thấy ít, sát mốc đóng băng → hủy H22, chỉ vá lỗi sai sự thật. *Chấp nhận, ghi vào giới hạn.*
- Khung docx có lỗi định dạng ẩn (danh mục rỗng, kiểu trích dẫn lệch) → đối chiếu mẫu, sinh lại bằng script có test. *Đã xử lý.*
- Dùng nhầm mẫu báo cáo cũ (khác bìa, lề trang) → đổi sang mẫu đúng của khoa. *Đang xử lý* (mục 8).
- Không có Word trên máy để kiểm file docx → kiểm cấu trúc XML bằng test và render bằng OnlyOffice; cập nhật mục lục làm tay. *Giảm thiểu.*


**Tin nhắn cho Hùng (bản 11/11, Đạt tự gửi; nếu đã gửi thì ghi ngày gửi vào đây):**
> Hùng ơi, mình đã ghép xong báo cáo 6 chương (H23) bằng script, Hùng không cần làm H23 nữa. Báo cáo sinh tự động từ các file `docs/report/*.md`, nên sửa gì thì sửa trong `.md` (nhớ `git pull` trước), đừng sửa thẳng file docx. Việc còn lại của Hùng: **H26 (hạn 20/11)** vẽ 4 hình Chương 3, lưu đúng tên `assets/diagrams/bi_encoder.png`, `cross_encoder.png`, `naive_rag.png`, `agentic_rag.png`; bỏ Hình 3.5 khỏi `chuong3_draft.md`; sửa 7 điểm của `activity.drawio` rồi xuất lại `activity.png`, xong báo mình build lại. **H24** slide bảo vệ và **H25** video demo, chi tiết trong `docs/sprints/2026-11-16-sprint6-hung.md`. Hùng trả lời giúp mình trước hết 13/11 nhé.
