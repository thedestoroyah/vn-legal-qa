# Bàn giao phiên làm việc (cập nhật 16/11/2026)

> Nhật ký của Đạt, track trong git từ 10/11. Bối cảnh ít đổi (đề tài, kiến trúc, quy tắc tập kiểm thử, lệnh): `AGENTS.md`. Claude Code tự nạp cả hai qua `IT_Project/CLAUDE.md` (thư mục cha, ngoài git), dù mở phiên ở `IT_Project/` hay `vn-legal-qa/`.
>
> Nếu ngày cập nhật ở trên cũ hơn `git log`, xem `git log -p -- docs/HANDOFF.md` trước khi tin file. Các nhật ký phiên cũ (05/11–11/11) đã dùng cho báo cáo tuần 12, 13 và đã bỏ khỏi file này; bản đầy đủ còn trong git (commit `be94b61`).
>
> **Quy tắc cập nhật (Đạt, 11/11):** khi Đạt yêu cầu cập nhật hoặc kiểm HANDOFF cho phiên mới: (1) rà lại **mọi mục cũ** (trạng thái, việc tiếp theo, prompt, kế hoạch) và sửa chỗ đã sai, không chỉ thêm mục mới ở cuối; (2) ghi **nhật ký của phiên** (commit, việc đã làm, số liệu, khó khăn và tình trạng, tiến độ PLAN) vào mục 6 để làm báo cáo tuần sau, trừ khi phiên đó đã được đưa vào báo cáo tuần; (3) đọc lại như một phiên mới chưa biết gì và kiểm đủ để làm tiếp.

## 1. Trạng thái

**Git:** thay đổi tới hết phiên 11/11 đã commit trên `main`; **phiên 16/11 chưa commit** (mục 6). Đạt tự push. Tag chỉ ở máy Đạt, chưa push: `ui-before-h22` (giao diện trước mọi sửa đổi), `h22-attempt` (bản giao diện H22 làm rồi bỏ). Test: **385 pass** (`.venv/bin/python -m pytest -q`; 43 test trong `tests/test_build_report.py`). Repo có ref lạ `refs/remotes/origin` (cùng trỏ một commit với `origin/main`, có lẽ do lệnh fetch HTTPS tạo ra), vô hại; xóa được bằng `git update-ref -d refs/remotes/origin`.

**Tiến độ `docs/PLAN.md`:** 74/79 hạng mục xong (94%), không tính 5 hạng mục đã gạch (hủy). Cách đếm: `[x]` chia cho `[x]` + `[ ]` không gạch ngang. Còn mở: Task 5 (rà soát, Turnitin), H23 (cập nhật trường, ký, xuất PDF), H24, H25, dòng mốc nộp. Task 2 (Docker) Đạt kiểm bằng trình duyệt 16/11, đã đánh dấu.

**Hùng:** không phản hồi từ 07/11. **Từ 16/11 Đạt nhận hết việc còn lại của Hùng** (H24 slide, H25 video; H26 đã làm 16/11). Không chờ Hùng nữa; nếu Hùng đẩy code thì vẫn dùng prompt "Pull việc của Hùng".

**Sprint 5 (05/11–15/11):** xong. Đạt làm thay các thẻ H17, H18, H21 của Hùng (sổ quyết định `.superpowers/sdd/2026-11-05-sprint5-hung/progress.md`).

**Sprint 6 (16/11–27/11, làm sớm được vì không phải tính năng mới):** plan `docs/superpowers/plans/2026-11-16-sprint6-dat.md`, ledger `.superpowers/sdd/2026-11-16-sprint6-dat/progress.md`; thẻ Hùng `docs/sprints/2026-11-16-sprint6-hung.md`. Task 1, 3, 4 xong; Task 2 chỉ còn Đạt mở giao diện bằng trình duyệt; Task 5 đã làm một phần ngày 16/11 (đối chiếu quy định, thêm mục theo sheet yêu cầu; chưa rà từng chương, mục 2). H22 (giao diện mới) đã hủy, chỉ giữ bản vá 2 lỗi hiển thị sai sự thật. H23 (ghép báo cáo) Đạt làm thay, xong phần script (mục 5). H26 Đạt làm thay 16/11.

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

0. **Đạt xem lại và commit việc phiên 16/11** (mục 6): đọc các đoạn mới viết (mục 1.4 đoạn cuối, mục 1.6, đoạn "Khả năng ứng dụng thực tế" ở 5.7, câu dẫn Hình 4.6–4.8), xem 4 hình Chương 3 và Hình 4.8, rồi dùng prompt "Commit việc mới" ở mục 4 (Phụ lục B đề cương đã đồng bộ với `PLAN.md`).
1. **Báo cáo tổng (`docs/report/final_52300098_52300106.docx`), hạn nộp ELIT trước ngày công bố hội đồng 1 tuần, chậm nhất 04/12:**
   1. ~~*Đối chiếu quy định*~~ xong 16/11 (kết quả ở mục 5 "Đối chiếu quy định").
   2. *Rà soát nội dung (Task 5 Sprint 6):* đọc toàn bộ 6 chương theo sheet Rubric và ô "Các lưu ý về nội dung bài làm" (mục 5), số liệu khớp `eval/results/`, tham chiếu chéo (mọi Hình, Bảng được nhắc theo số trong thân bài), chính tả; sửa ở `.md` rồi `python docs/report/build_report.py`. Đã xong 16/11: Chương 3 viết lại (bỏ từ cường điệu, sửa chỗ lệch code, 14 trích dẫn) và mọi Hình/Bảng đều được nhắc theo số. Còn: đọc lại Chương 1, 2, 4, 5, 6 theo Rubric, chính tả. Prompt ở mục 4.
   3. ~~*Hình còn thiếu*~~ xong 16/11 (Hình 3.1–3.4, Hình 4.8). Build `--strict` phải hết cảnh báo.
   4. *Hoàn thiện bản nộp:* **sửa chữ thì sửa ở `.md`, không sửa docx** (16/11 Đạt sửa tay docx, mình phải dò lại bằng diff và chép vào `.md`; bản đó lưu ở `IT_Project/submission/backup/final_dat_sua_tay_1611_1614.docx`). Mở docx bằng Word hoặc OnlyOffice (mục 5 "Cập nhật trường"), Ctrl+A rồi F9; kiểm chú thích, mục lục, danh mục hình/bảng ra đúng số; kiểm trang trắng trước Chương 1; ghi ngày, ký ở trang cảm ơn, cam đoan; xuất PDF; Turnitin (Đạt tự nộp).
   5. *Nộp:* `52300098_52300106.zip` lên ELIT. **Theo sheet "Thông tin môn học_DỰ ÁN" (đọc đủ 16/11), zip gồm:** báo cáo PDF; file scan kế hoạch có chữ ký GVHD; thư mục Source Code (đã bỏ thư mục thừa như `.venv/`, `node_modules`, `build`, cache) kèm thư viện/công cụ cần để chạy (nếu có) và **`readme.txt`** hướng dẫn chạy; `link.txt` nếu source ≥ 2 GB. Repo hiện chỉ có `README.md`: cần viết `readme.txt` (có thể rút từ README mục 1). `chroma_db.zip` (73 MB) để trong thư mục source hoặc ghi cách nạp lại chỉ mục trong `readme.txt`.
2. ~~**Task 2 Sprint 6**~~ xong 16/11 (Docker chạy được, đã `docker compose down`).
3. **H24 slide bảo vệ, H25 video demo (Đạt nhận từ 16/11, hạn trong PLAN 26/11):** chi tiết trong thẻ `docs/sprints/2026-11-16-sprint6-hung.md` (dàn ý 15–20 slide, 4 kịch bản video). Thuyết trình 15 phút, hội đồng hỏi 30 phút (sheet môn học). Ý tưởng slide ở mục 5.
4. **Báo cáo tuần 14 (16.11–22.11):** nội dung là các việc **từ phiên 12/11 trở đi** (mọi việc tới hết 11/11 đã nằm trong báo cáo tuần 13). Mỗi phiên ghi nhật ký vào mục 6. Prompt ở mục 4.
5. Còn treo, nhỏ: thẻ H22 mục 8 (gợi ý "đợi vài giây rồi bấm Thử lại" sai với lỗi 500, `src/ui/web/api/client.py`); 7 lỗi nhỏ của review đổi khung (ledger `.superpowers/sdd/2026-11-11-report-template-switch/progress.md`, dòng `minor (deferred)`), trong đó đáng xem: một ô ký "Tác giả" cho 2 người (chữ của mẫu, Đạt quyết), cột đầu bảng viết tắt hẹp. Tùy chọn: tắt số liệu ẩn danh của Impeccable (`IT_Project/.claude/skills/impeccable/scripts/impeccable telemetry off`).

## 3. Rủi ro và lỗi nhỏ còn hoãn

- **Quota:** Gemini 500 lượt/ngày/key, hay báo 503 "high demand" (lỗi phía Google, đã thử 2 mạng; dòng lỗi được chạy lại ở lần sau). Groq khoảng 100 lượt chấm/ngày/key. Quota Gemini hồi khoảng 14:20 giờ VN. Quay video demo khi mô hình ổn định.
- **Bộ chấm dễ dãi**: faithfulness ≈ 1 ở mọi cấu hình, kappa = 0 → chỉ số phụ, dựa chính vào citation P/R và đúng phiên bản.
- **Cỡ mẫu**: router chỉ có ý nghĩa ở đúng phiên bản; cần khoảng 390–1050 câu để recall/correctness có ý nghĩa → báo cáo là xu hướng.
- **Lỗi nhỏ, đã xếp loại 03/11:**
  - *Ghi vào báo cáo, không sửa* (sửa thì số liệu đổi): reranker `max_length=512` cắt 56/1.693 Điều; `version_correct` tính cả văn bản khác lĩnh vực; prompt chấm thiếu ví dụ 0 điểm.
  - *Bỏ qua:* `_safe_date` nhận "any" từ LLM; `agree` crash với ô "x"; `judge_results` hết quota chưa có test; `_SPLIT_RE` tách câu sai sau "Đ."; `drop_citations` mất chữ thường chung ngoặc; `ID_RE` không nhận mã `fixed`; `lost_sentences` lệch chỉ số; `agent_smoke.md` bị ghi đè; BLDS Điều 688–689 gán sai Chương (Chương không dùng khi embedding); `get_article` trả None trên biến thể `fixed`; 4 lỗi review Sprint 5 (`parse_categories` nhãn trùng, `sheet --tag`, `answer_sha` không gồm đáp án mẫu, `plots._mean` nhóm rỗng).
- **Docker:** chạy được trên máy Đạt (16/11). Chưa kiểm: tải mô hình trên máy sạch, chạy trên Windows.
- **Bộ nộp:** `IT_Project/submission/chroma_db.zip` (73 MB, 4 chỉ mục, ngoài repo, đã kiểm giải nén và truy xuất thật) đi trong zip nộp ELIT cùng source (mục 2 việc 1.5). Nếu nạp lại chỉ mục thì tạo lại: `python -c "import shutil; shutil.make_archive('../submission/chroma_db', 'zip', root_dir='.', base_dir='chroma_db')"` khi không có container nào đang chạy.
- **Tài liệu tham khảo:** 15 mục (mục 12 đề cương), đã tra nguồn 03/11 và 10/11, APA 7 trong `docs/report/tai_lieu_tham_khao.md`, có test kiểm trích dẫn ↔ danh mục. BM25 giữ 3(4) 333–389 (Crossref ghi 4(1-2) 1–174 là sai). Pham 2025 toàn văn: scitepress.org/Papers/2025/137354/137354.pdf; Nguyen Ba 2024 xếp hạng lại bằng câu trả lời LLM (Active Retrieval), không phải cross-encoder (đề cương mục 7 đã sửa).

## 4. Gợi ý prompt cho phiên mới

**Tiếp tục chung**
```
Tóm tắt trạng thái hiện tại và 3 việc nên làm tiếp. Chưa làm gì, chưa commit.
```

**Chạy Task 5 Sprint 6**
```
Chạy Task 5 của plan docs/superpowers/plans/2026-11-16-sprint6-dat.md (rà soát báo cáo), đọc ledger .superpowers/sdd/2026-11-16-sprint6-dat/progress.md và HANDOFF mục 5 (Đối chiếu quy định, Yêu cầu của môn) trước. Báo cáo sinh bằng python docs/report/build_report.py: sửa lỗi ở file .md rồi build lại. Turnitin tôi tự nộp. Không commit, báo tôi khi xong.
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

**Nguồn và lệnh:** 6 chương `docs/report/chuong1_draft.md` … `chuong6_draft.md`, phần đầu `docs/report/phan_dau.md` (Lời cảm ơn, Tóm tắt, Abstract, Viết tắt), tài liệu `docs/report/tai_lieu_tham_khao.md`. `python docs/report/build_report.py` (`--strict` thoát mã 1 nếu còn cảnh báo) ghi đè `docs/report/final_52300098_52300106.docx` (77 trang; nội dung Chương 1–6 là 64 trang, quy định 30–80; 0 cảnh báo từ 16/11). 42 test trong `tests/test_build_report.py`. Không sửa thẳng docx, trừ cập nhật trường và ký tên ở bản nộp.

**Khung:** dùng thẳng mẫu khoa `docs/managements/HƯỚNG DẪN BÁO CÁO/3. Template báo cáo/DỰ ÁN CNTT/TemplateCacMonDuAnVaThucTap_KhoaCNTT.dotx` (đổi 11/11; plan `docs/superpowers/plans/2026-11-11-report-template-switch.md`, ledger `.superpowers/sdd/2026-11-11-report-template-switch/progress.md`). Bìa điền bằng `FRONT_TEXT` trong `build_report.py`: tên SV theo MSSV (Đạt trước), chuyên ngành "KHOA HỌC MÁY TÍNH", GVHD "PGS.TS. Lê Anh Cường", năm 2026; không có trang xác nhận GV (mẫu không có); lề 3,5 / 2 / 3 / 3,5 cm; cam đoan xưng "chúng tôi"; ngày tháng, chữ ký để làm tay. Chữ mẫu nào không thấy thì build dừng (`ValueError`). Khung cũ `khung_TDTU.docx` và `docs/managements/Template_VN.dotx` là mẫu cũ, không dùng.

**Cập nhật trường (quan trọng):** OnlyOffice tính sai mọi trường số của chú thích: 11/11 `STYLEREF` ra "Error!…"; 16/11 (bản `SEQ \r N`) nó bỏ qua `\r`, đếm nối tiếp cả bài (Bảng 3.1 thành 3.3, Hình 4.1 thành 4.5) và danh mục hình mất số ("Hình 3.:"). Danh mục bảng ra "No table of figures entries found" vì mẫu khoa ghi `TOC \c "Bảng"` ở dạng Unicode tổ hợp (a + U+0309), không khớp "Bảng" dựng sẵn của SEQ (Word cũng sẽ lỗi). **Từ 16/11 (tối) chú thích không còn trường nào:** chữ "Hình 5.3: …" ghi sẵn, style riêng `CaptionHinh`/`CaptionBang` (tên "Chu thich Hinh"/"Chu thich Bang", dựa trên Caption), danh mục đổi thành `TOC \h \z \t "Chu thich Hinh,1"` / `"Chu thich Bang,1"` (hàm `caption_lists_by_style`, so khớp sau chuẩn hóa NFC). Test `test_caption_is_plain_text_in_its_own_style`, `test_caption_lists_built_from_caption_styles_numbering_styles_exist`; `test_caption_numbers_follow_chapter_and_order` giữ số trong Markdown đúng thứ tự (Markdown là số in ra). **Chưa kiểm `TOC \t` trên OnlyOffice GUI** (`x2t` không cập nhật trường): Đạt mở file, F9, xem danh mục hình và bảng. Nếu OnlyOffice không hỗ trợ `\t`, hướng tiếp theo: script tự sinh danh mục tĩnh kèm trường PAGEREF tới bookmark ở từng chú thích.

**Đối chiếu quy định (16/11)** với hướng dẫn trình bày kèm QĐ 2284 (`Huong dan trinh bay khoa luan TN, do an TN.docx`; bản PDF QĐ là ảnh scan, không trích được chữ), slide "Hướng dẫn trình bày văn bản" (mục lỗi thường gặp) và file Excel của môn:
- *Đã đúng sẵn:* lề 3,5/2/3/3,5 cm; Times New Roman 13; giãn 1,5 dòng; thụt đầu dòng 1 tab, căn đều; số trang giữa phía trên; tiểu mục tối đa 3 cấp, nhóm nào cũng ≥ 2 tiểu mục; số hình/bảng gắn số chương, chú thích bảng trên, hình dưới; hàng tiêu đề bảng lặp khi sang trang; danh mục viết tắt xếp ABC; trích dẫn tác giả–năm, "và cộng sự" khi ≥ 3 tác giả; ảnh giữ tỷ lệ.
- *Đã sửa:* danh mục tài liệu chia **A. Văn bản quy phạm pháp luật** (5 luật của kho, dạng "Tên (Luật số …) ngày …", theo ngày ban hành, có test đối chiếu `data/raw/laws.json`) và **B. Tài liệu tham khảo → Tiếng Anh**; danh mục giãn 1,5 dòng (trước là 2); tiêu đề Heading 1–4 dính đoạn sau (lỗi "treo tiêu đề"); lời cảm ơn ghi "PGS.TS." (lỗi "không ghi học hàm, học vị GVHD"); thêm nội dung sheet yêu cầu mà báo cáo thiếu: quản lý dự án, GitHub, kiểm thử (cuối 1.4), ý nghĩa khoa học và thực tiễn (1.6 mới, Bố cục thành 1.7), khả năng ứng dụng thực tế (5.7).
- *Còn lại cho Task 5:* rà văn phong, chính tả; kiểm khoảng trống lớn giữa trang (lỗi thường gặp) trên bản PDF cuối.

**Kiểm bằng ảnh:** `bash docs/managements/tools/topdf.sh "$PWD/docs/report/final_52300098_52300106.docx" <scratchpad>/r.pdf` rồi `pdftoppm`. OnlyOffice không có trang trắng trước Chương 1; Word chưa kiểm.

**Yêu cầu của môn** (sheet "Thông tin môn học_DỰ ÁN" và "Rubric" trong `docs/managements/HƯỚNG DẪN BÁO CÁO/Copy of QL. DỰ ÁN CNTT_ĐATN _KLTN.xlsx`, đọc đủ 16/11 bằng zipfile + ElementTree): môn Dự án CNTT (504091), 3 tín chỉ; điểm = 40% GK + 60% CK, CK = (HD + PB1 + PB2)/3; **nộp ELIT `MSSV1_MSSV2.zip`** (nội dung ở mục 2 việc 1.5) trước 1 tuần so với ngày công bố hội đồng phản biện, nộp trễ thì không được sửa hình thức, đạo văn; khoa kiểm đạo văn và thể thức; 2 GV phản biện độc lập, báo cáo trực tiếp, mang quyển báo cáo; thuyết trình 15 phút, trao đổi 30 phút. *Lưu ý nội dung* (ô B19): xác định vấn đề (ý nghĩa, khảo sát liên quan, mình làm gì khác), giải pháp có phương pháp luận (vì sao chọn), thực hiện (dữ liệu, code hiểu được), đánh giá (bộ test, độ đo, giải thích, **sẵn sàng ứng dụng thực tế**), **công cụ quản lý dự án** (team working, GitHub). *Rubric:* trừ điểm (sai tên GV/SV/khoa −1; lỗi diễn đạt, định dạng −1…+1; bố cục −1…+1; template sai (cấu trúc trang, mục lục, TLTK) −1; thiếu trích dẫn −1…+1; đạo văn > 20% từ −2) và 10 điểm chính: hiểu đề tài 5 (lý do, ý nghĩa 1; lý thuyết, khảo sát 2; code, xử lý dữ liệu 2), kết quả 5 (hàm lượng khoa học 2; chứng minh độ tin cậy 2; tính mới 1).

**Ý tưởng cho slide bảo vệ (H24):** cặp câu trả lời thật của M_016 trong `eval/results/agent_rq4.jsonl` (event trích BLLĐ 2012 Điều 22, current trích BLLĐ 2019 Điều 20 là văn bản chưa có hiệu lực năm 2020).

## 6. Nhật ký các phiên từ 12/11 (cho báo cáo tuần 14)

Mỗi phiên ghi: commit, việc đã làm, số liệu, khó khăn + tình trạng (Đã xử lý / Giảm thiểu / Chấp nhận, ghi vào giới hạn / Đang theo dõi), tiến độ PLAN.

### Nhật ký phiên 16/11

- **Commit:** chưa (Đạt xem rồi commit, mục 2 việc 0).
- **Đối chiếu quy định trình bày (việc 1.1 cũ):** đọc hướng dẫn trình bày kèm QĐ 2284, slide hướng dẫn của khoa, sheet môn học và Rubric. Kết quả và các chỗ đã sửa ở mục 5 "Đối chiếu quy định". Script `build_report.py`: tiêu đề dính đoạn sau, danh mục tài liệu giãn 1,5 dòng, chú thích bỏ STYLEREF (số chương ghi sẵn + `SEQ \r`). Test: 4 test mới (tiêu đề keepNext, phần A văn bản quy phạm pháp luật đối chiếu `laws.json`, chú thích không STYLEREF, số hình/bảng đúng thứ tự từng chương) và sửa 3 test cũ; 42 test báo cáo, toàn bộ 384 pass.
- **Nội dung báo cáo:** `tai_lieu_tham_khao.md` thêm phần A (5 luật) và nhóm "Tiếng Anh"; `phan_dau.md` ghi "PGS.TS."; Chương 1 thêm đoạn quản lý dự án (cuối 1.4) và mục 1.6 Ý nghĩa khoa học và thực tiễn; Chương 3 mục 3.7.2 bỏ sơ đồ chữ và Hình 3.5, dẫn sang Hình 4.2, sửa câu "hết lượt → trả lời giới hạn" thành "→ refuse" cho đúng code, thêm nút `refuse`; Chương 4 thêm câu dẫn Hình 4.6–4.8, Hình 4.8 (activity), ghi rõ chỉ sinh lại khi bật verify (b); Chương 5 mục 5.7 thêm "Khả năng ứng dụng thực tế" (số liệu từ `agent_rq3_ablation209.md`, `agent_rq3_latency.md`; khoảng 125 câu/ngày/key = 500 lượt / khoảng 4 lượt mỗi câu).
- **H26 (Đạt làm thay Hùng):** vẽ Hình 3.1–3.4 (`assets/diagrams/bi_encoder`, `cross_encoder`, `naive_rag`, `agentic_rag`, `.drawio` + `.png`) bằng script `IT_Project/tools/ch3_figures.py` (ngoài git, dùng lại `styled.py` của Hình 4.1–4.2); sửa `activity.drawio` theo 7 điểm của thẻ và thêm các chữ sai khác so với code (grade không lọc `relevant_ids`, khoảng hiệu lực `effective_date ≤ d < expiry_date`, lý do `insufficient` của refuse, rewrite thêm truy vấn chứ không thay; khi tắt verify (b) câu mất trích dẫn vẫn được gắn nhãn, chỉ không sinh lại); xuất lại `activity.png`, `activity.svg`.
- **Số liệu:** báo cáo 80 trang, nội dung Chương 1–6 là 67 trang (quy định 30–80); build 0 cảnh báo. Số liệu thực nghiệm không đổi.
- **Khó khăn + tình trạng:** Hùng không phản hồi từ 07/11 → Đạt nhận hết việc còn lại (H24, H25), H26 xong (Đã xử lý bằng cách nhận việc). Sơ đồ activity và Hình 3.x: Đã xử lý. Không có Word: Giảm thiểu (chú thích không còn phụ thuộc STYLEREF; còn phải mở OnlyOffice kiểm một lần). Bản PDF QĐ 2284 là ảnh scan: Giảm thiểu (dùng bản hướng dẫn .docx đi kèm). Zip nộp ELIT phải có source và `readme.txt`, HANDOFF cũ ghi thiếu: Đã xử lý (mục 2 việc 1.5). Docker trên Windows: Đang theo dõi (không còn người kiểm trên Windows). Gemini 503, giới hạn thực nghiệm, hủy giao diện mới: như tuần 13.
- **Tiến độ PLAN:** 74/79 (94%), +2 (H26, Task 2).
- **Chiều tối 16/11:** Đạt kiểm Docker (`docker compose up --build`) chạy tốt → Task 2 xong, đã tắt container. Đạt cập nhật trường bằng OnlyOffice thì danh mục bảng trống, số chú thích bị đánh lại sai → bỏ hẳn trường số ở chú thích, danh mục lấy theo style (mục 5 "Cập nhật trường"). Phát hiện lỗi cũ của build: comment `<!-- nguồn -->` ở cuối dòng bị xóa kèm dấu xuống dòng, làm **mất tiêu đề mục 5.6 "Phân tích lỗi"** (mục lục nhảy từ 5.5 sang "5.6 Thảo luận") và nối gạch đầu dòng cuối mục 5.4.5 vào đoạn trước; đã sửa `_COMMENT`, có test. Chép 2 chỗ Đạt sửa tay docx vào `.md` (bỏ "do Hùng xây dựng" ở 4.5, bỏ dòng "Tiếng Anh" ở danh mục tài liệu). Thử skill diagram-design (vẽ lại Hình 4.2) rồi gỡ cùng skill Taste: giữ bộ hình draw.io. Test 385 pass. Kiểm bằng script: 18 Hình/Bảng chưa được nhắc theo số (danh sách ở mục 2 việc 1.2); script: tìm chú thích `**Hình|Bảng X.Y.**` trong `chuong*_draft.md` rồi tìm "Hình X.Y" (hoặc khoảng "X.a–X.b") trong thân bài đã bỏ comment và dòng chú thích.
  - Khó khăn mới: OnlyOffice tính sai trường SEQ (Giảm thiểu: bỏ trường số; còn chờ Đạt kiểm `TOC \t`).
- **Tối 16/11, Task 5 (một phần):** viết lại Chương 3 (bản nháp của Hùng): bỏ khoảng 30 từ cường điệu; sửa chỗ lệch code: IDF của BM25 theo `rank_bm25.BM25Okapi` (không "+1", k1 = 1,5, b = 0,75, IDF âm thay bằng 0,25 × IDF trung bình), BGE-M3 giới hạn 2.048 token chứ không "8.192 giải quyết triệt để", tiêu đề phân cấp gắn vào đoạn là tên văn bản – Điều – tên Điều – Khoản (không có Chương), ví dụ cắt cố định 200/40 từ như RQ2, câu ngoài phạm vi theo prompt router, kiểm chứng trích dẫn có bước sinh lại rồi gắn nhãn, reranker giới hạn 512 token; bỏ câu nhắc Luật Ban hành văn bản quy phạm pháp luật (không có trong danh mục phần A); sửa công thức $P(A|Q,C)$; trích dẫn từ 9 lên 14 (thêm Robertson và Zaragoza 2009 cho công thức, Chen và cộng sự 2024, Asai/Yan/Pham cho Agentic-RAG, Reuter cho cách gắn tiêu đề). Thêm câu nhắc theo số cho 18 Hình/Bảng ở Chương 2–6. Báo cáo 77 trang, nội dung 64 trang; build 0 cảnh báo; 385 test pass.

Khó khăn còn mở từ báo cáo tuần 13 (để ghi tình trạng mới ở tuần 14): Hùng chưa cập nhật (Đang theo dõi); sơ đồ activity và Hình 3.x (Giảm thiểu, chờ H26); không có Word để kiểm docx (Giảm thiểu, nay thêm lỗi chú thích của OnlyOffice); Docker chưa kiểm trên Windows (Đang theo dõi); Gemini 503 (Giảm thiểu); các giới hạn thực nghiệm (Chấp nhận); hủy làm lại giao diện (Chấp nhận).

## 7. Công cụ và ghi chú

- **Báo cáo tuần:** `docs/managements/tools/README.md`. Mỗi tuần một thư mục `Week <dd.mm-dd.mm>/` có `content.json`, `build_pptx.js`, `build_xlsx.py` riêng; `build_docx.py` dùng chung. Môi trường tạm: venv có `python-docx`, `openpyxl`; `npm install pptxgenjs@3.12.0` rồi `NODE_PATH=<dir>/node_modules`. Mẫu Excel KLTN phải lấy bản `2a13ff0` (README đã ghi cách lấy). Slide tuần 13 nhận 2 ảnh (3 trang báo cáo, sơ đồ kiến trúc).
- **Sơ đồ draw.io:** `assets/diagrams/*.drawio` (architecture, agent_graph, usecase, sequence, activity, 4 hình Chương 3). Xuất PNG từ terminal VSCode phải bỏ biến `ELECTRON_RUN_AS_NODE`: `env -u ELECTRON_RUN_AS_NODE drawio -x -f png -s 2 -b 10 -o X.png X.drawio`. Ảnh cũ do AI vẽ (`architecture_old.png`, `agent_graph_old.png`) sai so với code, không dùng.
- `IT_Project/tools/` (ngoài git): `ui_shot.js` chụp giao diện bằng Electron: `env -u ELECTRON_RUN_AS_NODE electron44 ../tools/ui_shot.js http://127.0.0.1:8080/ OUT.png 1440 900 "ask:<câu hỏi>" "click:<chữ đầu của phần tử>" "wait:<ms>"`.
- Chạy giao diện không tốn quota (phát lại kết quả đã chạy): `LLM_API_KEY= UI_LOCAL_FALLBACK=1 API_URL=http://127.0.0.1:8999 .venv/bin/python -m src.ui.web.main`; tắt: `pkill -f '[s]rc\.ui\.web\.main'`.
- Skill Impeccable có hook (`IT_Project/.claude/settings.local.json`) chạy sau mỗi lần sửa file, trong phiên mở ở `IT_Project/`. Không dùng `live-server`/`live-inject` (sửa file của dự án).

- **Hình Chương 3:** `python3 IT_Project/tools/ch3_figures.py <thư mục ra>` sinh 4 file `.drawio` (rồi xuất PNG bằng lệnh drawio ở trên, `-s 2`). Sửa hình thì sửa script rồi chạy lại, chép `.drawio` và `.png` vào `assets/diagrams/`. `activity.drawio` sửa trực tiếp (script sửa ngày 16/11 nằm ở scratchpad, đã mất; file trong repo là bản cuối).
