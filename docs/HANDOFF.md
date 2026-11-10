# Bàn giao phiên làm việc (cập nhật 11/11/2026, tối)

> Nhật ký của Đạt, track trong git từ 10/11. Bối cảnh ít đổi (đề tài, kiến trúc, quy tắc tập kiểm thử, lệnh): `AGENTS.md`. Claude Code tự nạp cả hai qua `IT_Project/CLAUDE.md` (thư mục cha, ngoài git), dù mở phiên ở `IT_Project/` hay `vn-legal-qa/`.
>
> Nếu ngày cập nhật ở trên cũ hơn `git log`, xem `git log -p -- docs/HANDOFF.md` trước khi tin file. Các nhật ký phiên cũ (05/11–11/11) đã dùng cho báo cáo tuần 12, 13 và đã bỏ khỏi file này; bản đầy đủ còn trong git (commit `be94b61`).
>
> **Quy tắc cập nhật (Đạt, 11/11):** khi Đạt yêu cầu cập nhật hoặc kiểm HANDOFF cho phiên mới: (1) rà lại **mọi mục cũ** (trạng thái, việc tiếp theo, prompt, kế hoạch) và sửa chỗ đã sai, không chỉ thêm mục mới ở cuối; (2) ghi **nhật ký của phiên** (commit, việc đã làm, số liệu, khó khăn và tình trạng, tiến độ PLAN) vào mục 6 để làm báo cáo tuần sau, trừ khi phiên đó đã được đưa vào báo cáo tuần; (3) đọc lại như một phiên mới chưa biết gì và kiểm đủ để làm tiếp.

## 1. Trạng thái

**Git:** mọi thay đổi tới hết phiên 11/11 đã commit trên `main`; Đạt tự push. Tag chỉ ở máy Đạt, chưa push: `ui-before-h22` (giao diện trước mọi sửa đổi), `h22-attempt` (bản giao diện H22 làm rồi bỏ). Test: **381 pass** (`.venv/bin/python -m pytest -q`). Repo có ref lạ `refs/remotes/origin` (cùng trỏ một commit với `origin/main`, có lẽ do lệnh fetch HTTPS tạo ra), vô hại; xóa được bằng `git update-ref -d refs/remotes/origin`.

**Tiến độ `docs/PLAN.md`:** 72/79 hạng mục xong (91%), không tính 5 hạng mục đã gạch (hủy). Cách đếm: `[x]` chia cho `[x]` + `[ ]` không gạch ngang. Còn mở: Task 2 (Docker, chỉ còn mở trình duyệt), Task 5 (rà soát, Turnitin), H23 (chờ hình H26, cập nhật trường bằng Word), H24, H25, H26, dòng mốc nộp.

**Sprint 5 (05/11–15/11):** xong. Đạt làm thay các thẻ H17, H18, H21 của Hùng (sổ quyết định `.superpowers/sdd/2026-11-05-sprint5-hung/progress.md`).

**Sprint 6 (16/11–27/11, làm sớm được vì không phải tính năng mới):** plan `docs/superpowers/plans/2026-11-16-sprint6-dat.md`, ledger `.superpowers/sdd/2026-11-16-sprint6-dat/progress.md`; thẻ Hùng `docs/sprints/2026-11-16-sprint6-hung.md`. Task 1, 3, 4 xong; Task 2 chỉ còn Đạt mở giao diện bằng trình duyệt; Task 5 chưa làm. H22 (giao diện mới) đã hủy, chỉ giữ bản vá 2 lỗi hiển thị sai sự thật. H23 (ghép báo cáo) Đạt làm thay, xong phần script (mục 5).

**Báo cáo tuần:** tuần 12 (`docs/managements/Week 02.11-08.11/`) và **tuần 13** (`docs/managements/Week 09.11-15.11/`, ngày báo cáo 13/11/2026) đã xong, **không sửa nữa**. Báo cáo tuần 13 đã gồm mọi việc tới hết phiên 11/11 (cả việc 06/11, đổi khung báo cáo). **Đạt đã sửa tay 3 file tuần 13 sau khi build** nên `content.json` tuần 13 có thể không khớp hẳn với file đã nộp: khi làm tuần 14, đọc nội dung từ 3 file (docx, pptx, xlsx) nếu cần chính xác, đừng build lại tuần 13. Thư mục có thêm `report_preview.png` do Đạt tạo (ảnh 3 trang báo cáo, có lẽ thay ảnh slide 5).

**Bảng số liệu dùng cho báo cáo** (`eval/results/`): `retrieval_rq1.md`, `retrieval_rq2.md`, `agent_rq3_ablation209.md` (5 cấu hình, 209 câu), `agent_rq3_heldout30.md`, `agent_rq4.md` (32 câu temporal), `agent_rq4_heldout20.md`, `agent_rq3_latency.md` (19 câu; `no_verify` n=18), `errors_rq3.md`, `verify_attack.md`, `v1_vs_v2.md`. Hình: `docs/report/figures/`. Tác tử, prompt, tập kiểm thử không đổi từ 03/11: số liệu thực nghiệm giữ nguyên.

**Kết quả chính:**
- RQ1 (77 câu Zalo): hybrid+rerank Hit@5 0,844, Recall@10 0,872. RQ2: article 0,883/0,890 > clause_plain 0,857/0,872 ≈ clause_header 0,844/0,872 ≫ fixed 0,597/0,617.
- RQ3, 209 câu, so với full (* = khoảng tin cậy không chứa 0): no_router đúng phiên bản −0,250* (n=32), recall −0,034, correctness −0,042 (chưa ý nghĩa); baseline precision −0,060*, phiên bản −0,250*; no_verify recall +0,034*, precision −0,016*; no_grading không khác. → H1 được ủng hộ ở chỉ số đúng phiên bản. Verify là lớp phòng vệ: đổi recall lấy precision.
- Tập giữ riêng 30 câu: full P 0,978 / R 0,767 / phiên bản 0,700 / correctness 0,750; no_router kém cùng chiều (−0,143 / −0,133 / −0,200 / −0,083) nhưng chưa có ý nghĩa. full trả lời ít hơn no_router (0,767 vs 0,833).
- RQ4, 32 câu: current kém event −0,312* (recall, phiên bản); any kém −0,188 về phiên bản, sát ngưỡng [−0,375; 0,000]. → H2: event > current được ủng hộ, event > any chưa.
- Phép thử verify: bắt 46/47 mồi cùng ngữ cảnh, 50/50 mồi khác văn bản, 0 báo động nhầm.
- H14 (Đạt chấm 20 câu, `grading_rq3_dat.csv`): khớp faithfulness 0,950, correctness 0,917, nhưng bộ chấm cho 1 ở mọi câu nên kappa = 0. Báo cáo phải ghi: một người chấm, cũng là người làm hệ thống.

**Lịch sử thay đổi cần nêu trong báo cáo:** verify v1 gỡ nhầm 47/63 mã đúng → v2 thêm tiêu đề Điều vào prompt verify (gỡ 28, 21 đúng); router từ chối nhầm câu dân sự → sửa prompt. Prompt được chỉnh sau khi thấy lỗi trên tập kiểm thử; tập giữ riêng 30 câu soạn sau khi chốt prompt (commit `caa4f2f`) để giảm giới hạn này. M_017 do Hùng sửa câu hỏi ngày 03/11, đã chạy lại 5 cấu hình + 3 chính sách. Sửa `lookup_article` ngày 03/11 (tra cứu trực tiếp trả đúng Điều của văn bản đã hết hiệu lực, vd M_066) **không chạy lại thực nghiệm**: số liệu Chương 5 là của code tới `d8c459e`, đã ghi trong báo cáo. Router xếp nhầm 3/204 câu ra ngoài phạm vi: không sửa prompt, đã ghi vào giới hạn.

## 2. Việc tiếp theo

**Ưu tiên phiên tới** (theo thứ tự):

1. **Báo cáo tổng (`docs/report/final_52300098_52300106.docx`), hạn nộp ELIT trước ngày công bố hội đồng 1 tuần, chậm nhất 04/12:**
   1. *Đối chiếu quy định:* `docs/managements/HƯỚNG DẪN BÁO CÁO/2. Quy định và hướng dẫn/` (QĐ 2284, hướng dẫn trình bày: lề, cỡ chữ, giãn dòng, đánh số trang, chú thích, tài liệu tham khảo) + sheet "Thông tin môn học_DỰ ÁN" mục "Các lưu ý về nội dung bài làm" + sheet "Rubric" (mục 5). Sửa chỗ lệch ở `build_report.py` (có test) hoặc ở file `.md`. Lưu ý: mẫu khoa đã được dùng nguyên, đừng đổi bìa, lề nếu quy định không đòi.
   2. *Rà soát nội dung (Task 5 Sprint 6):* đọc toàn bộ 6 chương theo rubric, số liệu khớp `eval/results/`, tham chiếu chéo, chính tả; sửa ở `.md` rồi `python docs/report/build_report.py`. Prompt ở mục 4.
   3. *Hình còn thiếu:* Hình 3.1–3.4 và activity (H26 của Hùng, hạn 20/11); Hùng im lặng thì Đạt tự vẽ hoặc bỏ hình và sửa câu dẫn. Build `--strict` phải hết cảnh báo.
   4. *Hoàn thiện bản nộp:* mở docx bằng **Word** (không dùng OnlyOffice, mục 5 "Cập nhật trường"), Ctrl+A rồi F9; kiểm có trang trắng trước Chương 1 không; ghi ngày, ký ở trang cảm ơn, cam đoan; xuất PDF; Turnitin (Đạt tự nộp).
   5. *Nộp:* `52300098_52300106.zip` lên ELIT gồm báo cáo PDF, bản scan kế hoạch có chữ ký GVHD và các mục khác trong sheet "Thông tin môn học_DỰ ÁN" (đọc đủ ô "Nội dung nộp bài"). Repo và `chroma_db.zip` nộp 03/12 (mục 3).
2. **Task 2 Sprint 6:** Đạt chạy `docker compose up --build` một lần (phải `--build`: image trên máy đang chứa giao diện H22 đã hủy), thấy "Đã kết nối · gemini-3.1-flash-lite" thì đánh dấu Task 2 ở `PLAN.md` và Phụ lục B đề cương.
3. **Theo dõi Hùng** (không cập nhật gì từ 07/11): tin nhắn ở mục 7 (Đạt tự gửi; nếu đã gửi thì ghi ngày gửi). Khoảng 20/11 vẫn im lặng thì Đạt nhận H24 (slide). Khi Hùng đẩy code: dùng prompt "Pull việc của Hùng" ở mục 4.
4. **Báo cáo tuần 14 (16.11–22.11):** nội dung là các việc **từ phiên 12/11 trở đi** (mọi việc tới hết 11/11 đã nằm trong báo cáo tuần 13). Mỗi phiên ghi nhật ký vào mục 6. Prompt ở mục 4.
5. Còn treo, nhỏ: thẻ H22 mục 8 (gợi ý "đợi vài giây rồi bấm Thử lại" sai với lỗi 500, `src/ui/web/api/client.py`); 7 lỗi nhỏ của review đổi khung (ledger `.superpowers/sdd/2026-11-11-report-template-switch/progress.md`, dòng `minor (deferred)`), trong đó đáng xem: một ô ký "Tác giả" cho 2 người (chữ của mẫu, Đạt quyết), cột đầu bảng viết tắt hẹp. Tùy chọn: gỡ skill Taste (`rm -rf IT_Project/.agents/skills/design-taste-frontend`), tắt số liệu ẩn danh của Impeccable (`IT_Project/.claude/skills/impeccable/scripts/impeccable telemetry off`).

## 3. Rủi ro và lỗi nhỏ còn hoãn

- **Quota:** Gemini 500 lượt/ngày/key, hay báo 503 "high demand" (lỗi phía Google, đã thử 2 mạng; dòng lỗi được chạy lại ở lần sau). Groq khoảng 100 lượt chấm/ngày/key. Quota Gemini hồi khoảng 14:20 giờ VN. Quay video demo khi mô hình ổn định.
- **Bộ chấm dễ dãi**: faithfulness ≈ 1 ở mọi cấu hình, kappa = 0 → chỉ số phụ, dựa chính vào citation P/R và đúng phiên bản.
- **Cỡ mẫu**: router chỉ có ý nghĩa ở đúng phiên bản; cần khoảng 390–1050 câu để recall/correctness có ý nghĩa → báo cáo là xu hướng.
- **Lỗi nhỏ, đã xếp loại 03/11:**
  - *Ghi vào báo cáo, không sửa* (sửa thì số liệu đổi): reranker `max_length=512` cắt 56/1.693 Điều; `version_correct` tính cả văn bản khác lĩnh vực; prompt chấm thiếu ví dụ 0 điểm.
  - *Bỏ qua:* `_safe_date` nhận "any" từ LLM; `agree` crash với ô "x"; `judge_results` hết quota chưa có test; `_SPLIT_RE` tách câu sai sau "Đ."; `drop_citations` mất chữ thường chung ngoặc; `ID_RE` không nhận mã `fixed`; `lost_sentences` lệch chỉ số; `agent_smoke.md` bị ghi đè; BLDS Điều 688–689 gán sai Chương (Chương không dùng khi embedding); `get_article` trả None trên biến thể `fixed`; 4 lỗi review Sprint 5 (`parse_categories` nhãn trùng, `sheet --tag`, `answer_sha` không gồm đáp án mẫu, `plots._mean` nhóm rỗng).
- **Docker chưa kiểm:** nạp đủ chỉ mục trong container (đã thử 3 chunk), tải mô hình trên máy sạch, chạy trên Windows (nhờ Hùng).
- **Bộ nộp:** `IT_Project/submission/chroma_db.zip` (73 MB, 4 chỉ mục, ngoài repo, đã kiểm giải nén và truy xuất thật) nộp kèm repo ngày 03/12. Nếu nạp lại chỉ mục thì tạo lại: `python -c "import shutil; shutil.make_archive('../submission/chroma_db', 'zip', root_dir='.', base_dir='chroma_db')"` khi không có container nào đang chạy.
- **Tài liệu tham khảo:** 15 mục (mục 12 đề cương), đã tra nguồn 03/11 và 10/11, APA 7 trong `docs/report/tai_lieu_tham_khao.md`, có test kiểm trích dẫn ↔ danh mục. BM25 giữ 3(4) 333–389 (Crossref ghi 4(1-2) 1–174 là sai). Pham 2025 toàn văn: scitepress.org/Papers/2025/137354/137354.pdf; Nguyen Ba 2024 xếp hạng lại bằng câu trả lời LLM (Active Retrieval), không phải cross-encoder (đề cương mục 7 đã sửa).

## 4. Gợi ý prompt cho phiên mới

**Tiếp tục chung**
```
Tóm tắt trạng thái hiện tại và 3 việc nên làm tiếp. Chưa làm gì, chưa commit.
```

**Đối chiếu quy định trình bày (việc 1.1)**
```
Đọc HANDOFF mục 2 việc 1.1 và mục 5. Đối chiếu báo cáo tổng (python docs/report/build_report.py, render bằng docs/managements/tools/topdf.sh) với QĐ 2284, hướng dẫn trình bày và sheet Rubric trong docs/managements/HƯỚNG DẪN BÁO CÁO/. Liệt kê chỗ lệch kèm đề xuất sửa trước, chưa sửa, chưa commit.
```

**Chạy Task 5 Sprint 6**
```
Chạy Task 5 của plan docs/superpowers/plans/2026-11-16-sprint6-dat.md (rà soát báo cáo), đọc ledger .superpowers/sdd/2026-11-16-sprint6-dat/progress.md và sheet Rubric trước. Báo cáo sinh bằng python docs/report/build_report.py: sửa lỗi ở file .md rồi build lại. Turnitin tôi tự nộp. Không commit, báo tôi khi xong.
```

**Pull việc của Hùng**
```
Repo có cập nhật, pull về (theo CLAUDE.md), kiểm tra Hùng sửa gì, chạy test, báo xung đột với AGENTS.md (nhất là tập kiểm thử, prompt) rồi làm tiếp.
```

**Báo cáo tuần 14**
```
Đọc docs/managements/tools/README.md và docs/HANDOFF.md mục 1 (Báo cáo tuần), mục 6. Làm báo cáo tuần 14 (16.11-22.11) trong docs/managements/Week 16.11-22.11: chép content.json, build_pptx.js, build_xlsx.py của tuần 13 rồi sửa; cùng 4 chương, cùng thiết kế. Nội dung là việc từ 12/11 (mục 6 và git log, cả của Hùng). Khó khăn tuần 13 đã xong thì chuyển sang ch4.resolved, còn lại giữ nhãn tình trạng. Kiểm bằng ảnh render.
```

**Commit việc mới**
```
Commit giúp tôi các thay đổi chưa commit thành vài commit hợp lý (quét key trong diff trước). Tôi sẽ tự push.
```

## 5. Báo cáo cuối kỳ: cách sinh và yêu cầu nộp

**Nguồn và lệnh:** 6 chương `docs/report/chuong1_draft.md` … `chuong6_draft.md`, phần đầu `docs/report/phan_dau.md` (Lời cảm ơn, Tóm tắt, Abstract, Viết tắt), tài liệu `docs/report/tai_lieu_tham_khao.md`. `python docs/report/build_report.py` (`--strict` thoát mã 1 nếu còn cảnh báo) ghi đè `docs/report/final_52300098_52300106.docx` (khoảng 77 trang, hiện còn 5 cảnh báo thiếu Hình 3.1–3.5 chờ H26, ô "[CHỜ HÌNH 3.x: …]" trong file). 39 test trong `tests/test_build_report.py`. Không sửa thẳng docx, trừ cập nhật trường và ký tên ở bản nộp.

**Khung:** dùng thẳng mẫu khoa `docs/managements/HƯỚNG DẪN BÁO CÁO/3. Template báo cáo/DỰ ÁN CNTT/TemplateCacMonDuAnVaThucTap_KhoaCNTT.dotx` (đổi 11/11; plan `docs/superpowers/plans/2026-11-11-report-template-switch.md`, ledger `.superpowers/sdd/2026-11-11-report-template-switch/progress.md`). Bìa điền bằng `FRONT_TEXT` trong `build_report.py`: tên SV theo MSSV (Đạt trước), chuyên ngành "KHOA HỌC MÁY TÍNH", GVHD "PGS.TS. Lê Anh Cường", năm 2026; không có trang xác nhận GV (mẫu không có); lề 3,5 / 2 / 3 / 3,5 cm; cam đoan xưng "chúng tôi"; ngày tháng, chữ ký để làm tay. Chữ mẫu nào không thấy thì build dừng (`ValueError`). Khung cũ `khung_TDTU.docx` và `docs/managements/Template_VN.dotx` là mẫu cũ, không dùng.

**Cập nhật trường (quan trọng):** chú thích có trường `STYLEREF 1 \s` (số chương) + `SEQ`. Ngày 11/11 Đạt mở file bằng OnlyOffice, cập nhật trường rồi lưu: mục lục đúng nhưng **mọi chú thích thành "Hình Error! No text of specified style in document..6"** (OnlyOffice không tính được STYLEREF). Bản docx đang commit là bản đó; so với bản build mới thì chữ, ảnh, lề, đánh số trang giống hệt, chỉ khác kết quả trường, nên chạy lại `build_report.py` không mất gì. Bản nộp phải cập nhật trường bằng **Word**. Nếu không có Word: sửa `build_report.py` để chú thích không cần STYLEREF (vd ghi sẵn số chương, chỉ dùng `SEQ … \s 1`) rồi thử lại trên OnlyOffice; có test `test_caption_gets_chapter_and_seq_fields` cần sửa theo.

**Kiểm bằng ảnh:** `bash docs/managements/tools/topdf.sh "$PWD/docs/report/final_52300098_52300106.docx" <scratchpad>/r.pdf` rồi `pdftoppm`. OnlyOffice không có trang trắng trước Chương 1; Word chưa kiểm.

**Yêu cầu của môn** (sheet "Thông tin môn học_DỰ ÁN" trong `docs/managements/HƯỚNG DẪN BÁO CÁO/Copy of QL. DỰ ÁN CNTT_ĐATN _KLTN.xlsx`; đọc bằng zipfile + sharedStrings vì `.venv` chưa có openpyxl, ô dài mới đọc 150 ký tự đầu): môn Dự án CNTT (504091), 3 tín chỉ, nhóm tối đa 2 SV; giữa kỳ (sau 8 tuần) 40% điểm; **nộp ELIT file `MSSV1_MSSV2.zip`** gồm báo cáo PDF, file scan kế hoạch có chữ ký GVHD, … (đọc đủ ô "Nội dung nộp bài"), trước 1 tuần so với ngày công bố hội đồng phản biện; khoa kiểm tra đạo văn và thể thức trình bày; 2 GV phản biện, báo cáo trực tiếp, mang quyển báo cáo. **Chưa đọc đủ:** mục "Các lưu ý về nội dung bài làm", sheet "Rubric", QĐ 2284 và hướng dẫn trình bày (việc 1.1).

**Ý tưởng cho slide bảo vệ (H24):** cặp câu trả lời thật của M_016 trong `eval/results/agent_rq4.jsonl` (event trích BLLĐ 2012 Điều 22, current trích BLLĐ 2019 Điều 20 là văn bản chưa có hiệu lực năm 2020).

## 6. Nhật ký các phiên từ 12/11 (cho báo cáo tuần 14)

Chưa có phiên nào. Mỗi phiên ghi: commit, việc đã làm, số liệu, khó khăn + tình trạng (Đã xử lý / Giảm thiểu / Chấp nhận, ghi vào giới hạn / Đang theo dõi), tiến độ PLAN.

Khó khăn còn mở từ báo cáo tuần 13 (để ghi tình trạng mới ở tuần 14): Hùng chưa cập nhật (Đang theo dõi); sơ đồ activity và Hình 3.x (Giảm thiểu, chờ H26); không có Word để kiểm docx (Giảm thiểu, nay thêm lỗi chú thích của OnlyOffice); Docker chưa kiểm trên Windows (Đang theo dõi); Gemini 503 (Giảm thiểu); các giới hạn thực nghiệm (Chấp nhận); hủy làm lại giao diện (Chấp nhận).

## 7. Công cụ và ghi chú

- **Báo cáo tuần:** `docs/managements/tools/README.md`. Mỗi tuần một thư mục `Week <dd.mm-dd.mm>/` có `content.json`, `build_pptx.js`, `build_xlsx.py` riêng; `build_docx.py` dùng chung. Môi trường tạm: venv có `python-docx`, `openpyxl`; `npm install pptxgenjs@3.12.0` rồi `NODE_PATH=<dir>/node_modules`. Mẫu Excel KLTN phải lấy bản `2a13ff0` (README đã ghi cách lấy). Slide tuần 13 nhận 2 ảnh (3 trang báo cáo, sơ đồ kiến trúc).
- **Sơ đồ draw.io:** `assets/diagrams/*.drawio` (architecture, agent_graph, usecase, sequence; activity chờ H26). Xuất PNG từ terminal VSCode phải bỏ biến `ELECTRON_RUN_AS_NODE`: `env -u ELECTRON_RUN_AS_NODE drawio -x -f png -s 2 -b 10 -o X.png X.drawio`. Ảnh cũ do AI vẽ (`architecture_old.png`, `agent_graph_old.png`) sai so với code, không dùng.
- `IT_Project/tools/` (ngoài git): `ui_shot.js` chụp giao diện bằng Electron: `env -u ELECTRON_RUN_AS_NODE electron44 ../tools/ui_shot.js http://127.0.0.1:8080/ OUT.png 1440 900 "ask:<câu hỏi>" "click:<chữ đầu của phần tử>" "wait:<ms>"`.
- Chạy giao diện không tốn quota (phát lại kết quả đã chạy): `LLM_API_KEY= UI_LOCAL_FALLBACK=1 API_URL=http://127.0.0.1:8999 .venv/bin/python -m src.ui.web.main`; tắt: `pkill -f '[s]rc\.ui\.web\.main'`.
- Skill Impeccable có hook (`IT_Project/.claude/settings.local.json`) chạy sau mỗi lần sửa file, trong phiên mở ở `IT_Project/`. Không dùng `live-server`/`live-inject` (sửa file của dự án).

**Tin nhắn cho Hùng (bản 11/11, Đạt tự gửi; nếu đã gửi thì ghi ngày gửi vào đây):**
> Hùng ơi, mình đã ghép xong báo cáo 6 chương (H23) bằng script, Hùng không cần làm H23 nữa. Báo cáo sinh tự động từ các file `docs/report/*.md`, nên sửa gì thì sửa trong `.md` (nhớ `git pull` trước), đừng sửa thẳng file docx. Việc còn lại của Hùng: **H26 (hạn 20/11)** vẽ 4 hình Chương 3, lưu đúng tên `assets/diagrams/bi_encoder.png`, `cross_encoder.png`, `naive_rag.png`, `agentic_rag.png`; bỏ Hình 3.5 khỏi `chuong3_draft.md`; sửa 7 điểm của `activity.drawio` rồi xuất lại `activity.png`, xong báo mình build lại (Đạt thêm `<!-- Hình 4.8: assets/diagrams/activity.png -->` và chú thích vào Chương 4). **H24** slide bảo vệ và **H25** video demo, chi tiết trong `docs/sprints/2026-11-16-sprint6-hung.md`. Hùng trả lời giúp mình trước hết 13/11 nhé.
