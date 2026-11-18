# Bàn giao phiên làm việc (cập nhật 19/11/2026, rạng sáng)

> Nhật ký của Đạt, track trong git từ 10/11. Bối cảnh ít đổi (đề tài, kiến trúc, quy tắc tập kiểm thử, lệnh): `AGENTS.md`. Claude Code tự nạp cả hai qua `IT_Project/CLAUDE.md` (thư mục cha, ngoài git), dù mở phiên ở `IT_Project/` hay `vn-legal-qa/`.
>
> Nếu ngày cập nhật ở trên cũ hơn `git log`, xem `git log -p -- docs/HANDOFF.md` trước khi tin file. Các nhật ký phiên cũ (05/11–19/11) đã dùng cho báo cáo tuần 12, 13, 14 và đã bỏ khỏi file này; bản 05/11–11/11 còn trong git (commit `be94b61`), bản 16/11 ở commit `c2771a2`.
>
> **Quy tắc cập nhật (Đạt, 11/11):** khi Đạt yêu cầu cập nhật hoặc kiểm HANDOFF cho phiên mới: (1) rà lại **mọi mục cũ** (trạng thái, việc tiếp theo, prompt, kế hoạch) và sửa chỗ đã sai, không chỉ thêm mục mới ở cuối; (2) ghi **nhật ký của phiên** (commit, việc đã làm, số liệu, khó khăn và tình trạng, tiến độ PLAN) vào mục 6 để làm báo cáo tuần sau, trừ khi phiên đó đã được đưa vào báo cáo tuần; (3) đọc lại như một phiên mới chưa biết gì và kiểm đủ để làm tiếp.

## 1. Trạng thái

**Git:** mọi thay đổi tới hết phiên 19/11 đã commit trên `main` (`git log --oneline --since=2026-11-16`); Đạt tự push. Tag chỉ ở máy Đạt, chưa push: `ui-before-h22` (giao diện trước mọi sửa đổi), `h22-attempt` (bản giao diện H22 làm rồi bỏ). Test: **393 pass** (`.venv/bin/python -m pytest -q`; 51 test trong `tests/test_build_report.py`). Repo có ref lạ `refs/remotes/origin` (cùng trỏ một commit với `origin/main`, do lệnh fetch HTTPS tạo ra), vô hại; xóa được bằng `git update-ref -d refs/remotes/origin`.

**Tiến độ `docs/PLAN.md`:** 75/79 hạng mục xong (95%), không tính 5 hạng mục đã gạch (hủy). Cách đếm: `[x]` chia cho `[x]` + `[ ]` không gạch ngang. Còn mở: Task 5 (chỉ còn Turnitin), H23 (cập nhật mục lục, ký, xuất PDF), H25 (video demo), dòng mốc nộp. PLAN và Phụ lục B đề cương đang khớp.

**Hùng:** không phản hồi từ 07/11. **Từ 16/11 Đạt nhận hết việc còn lại của Hùng** (H24 xong, H25 Đạt tự quay, H26 xong). Không chờ Hùng nữa; nếu Hùng đẩy code thì dùng prompt "Pull việc của Hùng".

**Sprint 5 (05/11–15/11):** xong. Đạt làm thay các thẻ H17, H18, H21 của Hùng (sổ quyết định `.superpowers/sdd/2026-11-05-sprint5-hung/progress.md`).

**Sprint 6 (16/11–27/11):** plan `docs/superpowers/plans/2026-11-16-sprint6-dat.md`, ledger `.superpowers/sdd/2026-11-16-sprint6-dat/progress.md`; thẻ Hùng `docs/sprints/2026-11-16-sprint6-hung.md`. Task 1–4 xong (Task 2 Docker: Đạt kiểm bằng trình duyệt 16/11). Task 5: đối chiếu quy định, viết lại Chương 3, nhắc đủ Hình/Bảng theo số; Đạt đọc lại toàn bộ báo cáo 16/11 và đồng ý; 18/11 chỉnh trình bày (bảng cỡ 13, bỏ in đậm thân bài, viết lại văn phong); còn Turnitin. H22 đã hủy. H23, H24, H26 Đạt làm thay. 19/11 Đạt xác nhận bản docx hiện tại ổn.

**Báo cáo tuần:** tuần 12 (`docs/managements/Week 02.11-08.11/`), tuần 13 (`Week 09.11-15.11/`, ngày báo cáo 13/11) và tuần 14 (`Week 16.11-22.11/`, ngày báo cáo ghi 19/11/2026, gồm mọi việc từ sau báo cáo tuần 13 tới hết 19/11) đã xong, **không sửa nữa**. **Đạt đã sửa tay 3 file tuần 13 và 3 file tuần 14 sau khi build** nên `content.json` hai tuần này có thể không khớp hẳn với file đã nộp: khi cần nội dung chính xác, đọc từ 3 file (docx, pptx, xlsx), đừng build lại. **Tuần 15 (23.11–29.11) chưa làm**; nội dung là nhật ký mục 6 (ghi từ phiên sau 19/11).

**Bảng số liệu dùng cho báo cáo** (`eval/results/`): `retrieval_rq1.md`, `retrieval_rq2.md`, `agent_rq3_ablation209.md` (5 cấu hình, 209 câu), `agent_rq3_heldout30.md`, `agent_rq4.md` (32 câu temporal), `agent_rq4_heldout20.md`, `agent_rq3_latency.md` (19 câu; `no_verify` n=18), `errors_rq3.md`, `verify_attack.md`, `v1_vs_v2.md`. Hình: `docs/report/figures/`. Tác tử, prompt, tập kiểm thử không đổi từ 03/11: số liệu thực nghiệm giữ nguyên.

**Kết quả chính:**
- RQ1 (77 câu Zalo): hybrid+rerank Hit@5 0,844, Recall@10 0,872. RQ2: article 0,883/0,890 > clause_plain 0,857/0,872 ≈ clause_header 0,844/0,872 ≫ fixed 0,597/0,617.
- RQ3, 209 câu, so với full (* = khoảng tin cậy không chứa 0): no_router đúng phiên bản −0,250* (n=32), recall −0,034, correctness −0,042 (chưa ý nghĩa); baseline precision −0,060*, phiên bản −0,250*; no_verify recall +0,034*, precision −0,016*; no_grading không khác. → H1 được ủng hộ ở chỉ số đúng phiên bản. Verify là lớp phòng vệ: đổi recall lấy precision.
- Tập giữ riêng 30 câu: full P 0,978 / R 0,767 / phiên bản 0,700 / correctness 0,750; no_router kém cùng chiều (−0,143 / −0,133 / −0,200 / −0,083) nhưng chưa có ý nghĩa. full trả lời ít hơn no_router (0,767 vs 0,833).
- RQ4, 32 câu: current kém event −0,312* (recall, phiên bản); any kém −0,188 về phiên bản, sát ngưỡng [−0,375; 0,000]. → H2: event > current được ủng hộ, event > any chưa.
- Phép thử verify: bắt 46/47 mồi cùng ngữ cảnh, 50/50 mồi khác văn bản, 0 báo động nhầm.
- H14 (Đạt chấm 20 câu, `grading_rq3_dat.csv`): khớp faithfulness 0,950, correctness 0,917, nhưng bộ chấm cho 1 ở mọi câu nên kappa = 0. Báo cáo ghi: một người chấm, cũng là người làm hệ thống.

**Lịch sử thay đổi cần nêu trong báo cáo (đã nêu):** verify v1 gỡ nhầm 47/63 mã đúng → v2 thêm tiêu đề Điều vào prompt verify (gỡ 28, 21 đúng); router từ chối nhầm câu dân sự → sửa prompt. Prompt được chỉnh sau khi thấy lỗi trên tập kiểm thử; tập giữ riêng 30 câu soạn sau khi chốt prompt (commit `caa4f2f`). M_017 do Hùng sửa câu hỏi ngày 03/11, đã chạy lại. Sửa `lookup_article` ngày 03/11 **không chạy lại thực nghiệm**: số liệu Chương 5 là của code tới `d8c459e`. Router xếp nhầm 3/204 câu ra ngoài phạm vi: không sửa prompt, đã ghi vào giới hạn.

## 2. Việc tiếp theo

**Ưu tiên phiên tới** (theo thứ tự):

1. **Sửa công cụ render PDF (làm trước, mất vài phút):** `docs/managements/tools/topdf.sh` đang hỏng từ 19/11 (x2t báo `DoctRenderer: error code="calculate"`) vì Đạt đổi gói font hệ thống nên bộ đệm font cũ của OnlyOffice trỏ sai file. Mở OnlyOffice Desktop một lần để nó tạo lại bộ đệm rồi thử `bash docs/managements/tools/topdf.sh "$PWD/docs/report/final_52300098_52300106.docx" <scratchpad>/r.pdf`; chi tiết và cách vá tạm ở `docs/managements/tools/README.md` (cuối file). Chưa sửa thì `build_report.py` vẫn build được nhưng chỉ cảnh báo, để trống số trang trong danh mục hình/bảng (số ghi sẵn trong bản docx hiện tại là đúng).
2. **Kiểm bản báo cáo trước khi xuất PDF (Đạt):** mở `docs/report/final_52300098_52300106.docx` (bản commit `cb0bed8`), Ctrl+A rồi F9 để cập nhật mục lục (danh mục hình/bảng là danh mục tĩnh có trường PAGEREF, F9 chưa thử trên danh mục tĩnh bằng OnlyOffice GUI; nếu F9 làm sai số trang thì giữ số ghi sẵn, đang đúng); kiểm trang trắng trước Chương 1 và khoảng trống giữa trang trên bản PDF cuối, tốt nhất mở bằng Word.
3. **H25 video demo (Đạt tự quay):** 4 kịch bản ở thẻ `docs/sprints/2026-11-16-sprint6-hung.md` mục H25 (cũng ở `readme.txt` mục 5); quay lúc Gemini ổn định, trước khi quay mở `http://localhost:8000/health` phải thấy `"status":"ok"`. Slide 10 dùng video làm phương án dự phòng khi demo trực tiếp lỗi.
4. **Hoàn thiện bản nộp (Đạt):**
   - **Sửa chữ thì sửa ở `.md` rồi build lại, không sửa docx.** Trước khi build lại, kiểm Đạt có sửa tay docx không (so với commit; đã có lần 16/11, bản lưu ở `IT_Project/submission/backup/final_dat_sua_tay_1611_1614.docx`; `final_truoc_sua_1811.docx` là bản trước đợt chỉnh 18/11; `final_dat_sua_tay_1911.docx` là bản Đạt sửa tay tới 19/11).
   - Ghi ngày, ký ở trang cảm ơn và cam đoan (một ô "Tác giả" cho 2 người: ghi đủ tên cả hai); xuất PDF; nộp Turnitin; scan kế hoạch có chữ ký GVHD.
   - Tập nói theo slide một lượt bấm giờ (lời thuyết trình khoảng 12 phút; giới hạn 15 phút gồm demo).
5. **Báo cáo tuần 15 (23.11–29.11):** nội dung là nhật ký mục 6 (chưa có mục nào; ghi từ phiên sau 19/11) và `git log` từ 19/11. Hỏi Đạt ngày báo cáo (tuần 13 báo cáo thứ Năm 13/11, tuần 14 ghi 19/11). Prompt ở mục 4.
6. **Đóng gói nộp ELIT (làm cuối):** một file `52300098_52300106.zip` gồm báo cáo PDF, scan kế hoạch, thư mục source. Source lấy bằng `git archive HEAD` (tự bỏ `.venv/`, `.cache/`, `chroma_db/`, thư mục Zalo 287 MB vì đã ignore), thêm `IT_Project/submission/chroma_db.zip`; `readme.txt` có sẵn ở gốc repo. Hạn: trước 1 tuần so với ngày công bố hội đồng, chậm nhất 23:59 04/12. Prompt ở mục 4.
7. Còn treo, nhỏ: tùy chọn tắt số liệu ẩn danh của Impeccable (`IT_Project/.claude/skills/impeccable/scripts/impeccable telemetry off`). Các lỗi nhỏ còn lại của review đổi khung (M2–M4, M6 trong ledger `.superpowers/sdd/2026-11-11-report-template-switch/progress.md`) không ảnh hưởng bản nộp.

## 3. Rủi ro và lỗi nhỏ còn hoãn

- **`topdf.sh` hỏng do bộ đệm font OnlyOffice cũ** (mục 2 việc 1); chưa render lại được PDF kiểm bằng ảnh cho tới khi sửa.
- **F9 trên danh mục hình/bảng tĩnh chưa thử bằng OnlyOffice GUI** (mục 2 việc 2); số trang ghi sẵn đã khớp bản render 19/11.
- **Quota:** Gemini 500 lượt/ngày/key, hay báo 503 "high demand" (lỗi phía Google). Groq khoảng 100 lượt chấm/ngày/key. Quota Gemini hồi khoảng 14:20 giờ VN. Quay video demo khi mô hình ổn định.
- **Bộ chấm dễ dãi**: faithfulness ≈ 1 ở mọi cấu hình, kappa = 0 → chỉ số phụ, dựa chính vào citation P/R và đúng phiên bản.
- **Cỡ mẫu**: router chỉ có ý nghĩa ở đúng phiên bản; cần khoảng 390–1050 câu để recall/correctness có ý nghĩa → báo cáo là xu hướng.
- **Lỗi nhỏ, đã xếp loại 03/11:**
  - *Ghi vào báo cáo, không sửa* (sửa thì số liệu đổi): reranker `max_length=512` cắt 56/1.693 Điều; `version_correct` tính cả văn bản khác lĩnh vực; prompt chấm thiếu ví dụ 0 điểm.
  - *Bỏ qua:* `_safe_date` nhận "any" từ LLM; `agree` crash với ô "x"; `judge_results` hết quota chưa có test; `_SPLIT_RE` tách câu sai sau "Đ."; `drop_citations` mất chữ thường chung ngoặc; `ID_RE` không nhận mã `fixed`; `lost_sentences` lệch chỉ số; `agent_smoke.md` bị ghi đè; BLDS Điều 688–689 gán sai Chương (Chương không dùng khi embedding); `get_article` trả None trên biến thể `fixed`; 4 lỗi review Sprint 5 (`parse_categories` nhãn trùng, `sheet --tag`, `answer_sha` không gồm đáp án mẫu, `plots._mean` nhóm rỗng).
- **Docker:** chạy được trên máy Đạt (16/11). Chưa kiểm: tải mô hình trên máy sạch, chạy trên Windows (không còn người kiểm). Lần chạy đầu tải khoảng 7 GB mô hình (`readme.txt` đã ghi).
- **Chưa có Word:** chưa biết có trang trắng trước Chương 1 khi mở bằng Word (OnlyOffice không có); slide mới xem qua bản render OnlyOffice, chưa mở bằng PowerPoint. Từ 19/11 máy có Times New Roman và Consolas thật (gói `ttf-ms-win11-auto`), nên bản render gần Word hơn trước.
- **Bộ nộp:** `IT_Project/submission/chroma_db.zip` (73 MB, 4 chỉ mục, ngoài repo, đã kiểm giải nén và truy xuất thật). Nếu nạp lại chỉ mục thì tạo lại: `python -c "import shutil; shutil.make_archive('../submission/chroma_db', 'zip', root_dir='.', base_dir='chroma_db')"` khi không có container nào đang chạy.
- **Tài liệu tham khảo:** phần A 5 luật của kho; phần B 15 tài liệu (mục 12 đề cương), đã tra nguồn 03/11 và 10/11, APA 7 trong `docs/report/tai_lieu_tham_khao.md`, có test kiểm trích dẫn ↔ danh mục. BM25 giữ 3(4) 333–389 (Crossref ghi 4(1-2) 1–174 là sai). Câu về Cormack và cộng sự (2009) cố định k = 60 sau thử nghiệm sơ bộ (Chương 3) viết theo trí nhớ, chưa mở lại bài gốc.

## 4. Gợi ý prompt cho phiên mới

**Tiếp tục chung**
```
Tóm tắt trạng thái hiện tại và 3 việc nên làm tiếp. Chưa làm gì, chưa commit.
```

**Báo cáo tuần 15**
```
Đọc docs/managements/tools/README.md và docs/HANDOFF.md mục 1 (Báo cáo tuần), mục 6. Làm báo cáo tuần 15 (23.11-29.11) trong docs/managements/Week 23.11-29.11: chép content.json, build_pptx.js, build_xlsx.py của tuần 14 (lấy bản git, không phải bản Đạt sửa tay) rồi sửa; cùng 4 chương, cùng thiết kế. Nội dung là nhật ký mục 6 và git log từ 19/11. Khó khăn còn mở ở mục 6 giữ nhãn tình trạng, cái nào xong thì chuyển sang ch4.resolved. Hỏi tôi ngày báo cáo. Kiểm bằng ảnh render.
```

**Render PDF lỗi (`error code="calculate"`)**
```
topdf.sh báo lỗi calculate. Đọc docs/managements/tools/README.md (đoạn cuối về bộ đệm font OnlyOffice) và docs/HANDOFF.md mục 2 việc 1. Kiểm bộ đệm font đã tạo lại chưa, nếu chưa thì vá tạm trong thư mục scratchpad (không sửa dữ liệu OnlyOffice của tôi), rồi render thử báo cáo. Không commit.
```

**Sửa nội dung báo cáo**
```
Sửa báo cáo theo góp ý sau: ... Sửa ở docs/report/chuong*_draft.md, phan_dau.md, tai_lieu_tham_khao.md (không sửa docx), theo "Quy ước viết báo cáo" trong AGENTS.md; kiểm docx hiện tại có bị tôi sửa tay không trước khi build; chạy python docs/report/build_report.py --strict và pytest; kiểm bảng bằng ảnh render. Không commit.
```

**Sửa slide bảo vệ**
```
Sửa slide bảo vệ theo góp ý sau: ... Sửa trong docs/defense/build_slides.js (lệnh build ở HANDOFF mục 7), build lại, kiểm bằng ảnh render, báo tổng thời lượng lời nói.
```

**Đóng gói nộp ELIT**
```
Đóng gói bản nộp ELIT theo HANDOFF mục 2 việc 6: thư mục ../submission/52300098_52300106/ gồm báo cáo PDF tôi đã xuất (đường dẫn: ...), scan kế hoạch (đường dẫn: ...), thư mục source từ git archive HEAD kèm chroma_db.zip; kiểm readme.txt, giải nén thử, rồi nén thành 52300098_52300106.zip. Không commit.
```

**Pull việc của Hùng**
```
Repo có cập nhật, pull về (theo CLAUDE.md), kiểm tra Hùng sửa gì, chạy test, báo xung đột với AGENTS.md (nhất là tập kiểm thử, prompt) rồi làm tiếp.
```

**Commit việc mới**
```
Commit giúp tôi các thay đổi chưa commit thành vài commit hợp lý (quét key trong diff trước). Tôi sẽ tự push.
```

## 5. Báo cáo cuối kỳ: cách sinh và yêu cầu nộp

**Nguồn và lệnh:** 6 chương `docs/report/chuong1_draft.md` … `chuong6_draft.md`, phần đầu `docs/report/phan_dau.md` (Lời cảm ơn, Tóm tắt, Abstract, Viết tắt), tài liệu `docs/report/tai_lieu_tham_khao.md`. `python docs/report/build_report.py` (`--strict` thoát mã 1 nếu còn cảnh báo) ghi đè `docs/report/final_52300098_52300106.docx` (76 trang; nội dung Chương 1–6 khoảng 64 trang, quy định 30–80; 0 cảnh báo). 51 test trong `tests/test_build_report.py`. Không sửa thẳng docx, trừ cập nhật trường và ký tên ở bản nộp.

**Khung:** dùng thẳng mẫu khoa `docs/report/HƯỚNG DẪN BÁO CÁO/3. Template báo cáo/DỰ ÁN CNTT/TemplateCacMonDuAnVaThucTap_KhoaCNTT.dotx` (đổi 11/11; plan `docs/superpowers/plans/2026-11-11-report-template-switch.md`). Bìa điền bằng `FRONT_TEXT` trong `build_report.py`: tên SV theo MSSV (Đạt trước), chuyên ngành "KHOA HỌC MÁY TÍNH", GVHD "PGS.TS. Lê Anh Cường", năm 2026; không có trang xác nhận GV (mẫu không có); lề 3,5 / 2 / 3 / 3,5 cm; cam đoan xưng "chúng tôi"; ngày tháng, chữ ký để làm tay. Chữ mẫu nào không thấy thì build dừng (`ValueError`).

**Cập nhật trường và danh mục (quan trọng):** OnlyOffice tính sai mọi trường số của chú thích (11/11 `STYLEREF` ra "Error!…"; 16/11 bản `SEQ \r N` bị bỏ qua `\r`, đếm nối tiếp cả bài), và mẫu khoa ghi `TOC \c "Bảng"` ở dạng Unicode tổ hợp (a + U+0309) nên danh mục bảng trống. Hiện tại: **chú thích không có trường nào** (chữ "Hình 5.3: …" ghi sẵn, style `CaptionHinh`/`CaptionBang`, số trong Markdown là số in ra, `test_caption_numbers_follow_chapter_and_order` giữ đúng thứ tự). **`TOC \t` theo style cũng không chạy trên OnlyOffice (F9 để trống)**, nên từ 19/11 `build_report.py` tự sinh **danh mục tĩnh**: `bookmark_captions` đặt dấu trang `_Cap_<Hinh|Bang>_<chương>_<số>` quanh mỗi chú thích, `static_caption_lists` thay hai trường TOC bằng các dòng (chữ chú thích, dấu chấm dẫn, trường `PAGEREF`), `fill_caption_pages` render PDF bằng `topdf.sh` + `pdftotext` rồi build lại tới khi số trang ổn định (`caption_pages` đọc số trang in ở dòng đầu mỗi trang, lấy lần xuất hiện cuối của nhãn). Thiếu `topdf.sh`/`pdftotext` hoặc render lỗi thì cảnh báo và để trống số trang. Mục lục vẫn là trường TOC, cập nhật bằng F9.

**Chia cột bảng (18/11):** chữ bảng 13pt (style `BangNoiDung`). `_fit_columns` chia bề rộng theo từ dài nhất của ô: chữ số, chữ hoa, `@`, `%` và chữ code (`VerbatimChar`, Consolas) tính rộng hơn chữ thường; bảng nhiều cột không đủ chỗ thì thân bảng được ưu tiên (số liệu không bị bẻ), tiêu đề dài xuống dòng, tiêu đề cột Bảng 5.4 "Faithfulness", "Correctness" có gạch nối mềm (U+00AD) trong Markdown. Ô bảng không nên chứa token code dài không ngắt được (Bảng 4.2 từng phải bỏ mã `[BLLD2019_Dieu20_Khoan1]`). Bảng mới thêm vào thì xem ảnh render xem có chữ bị bẻ giữa từ không.

**Quy ước viết:** xem "Quy ước viết báo cáo" trong `AGENTS.md` (không in đậm thân bài và ô bảng, không `---`, không mũi tên). Sửa văn xuôi thì dùng skill `vn-humanizer` (skill cá nhân của Đạt ở `~/.claude/skills/`).

**Đối chiếu quy định (16/11)** với hướng dẫn trình bày kèm QĐ 2284 (`Huong dan trinh bay khoa luan TN, do an TN.docx`; bản PDF QĐ là ảnh scan), slide "Hướng dẫn trình bày văn bản" (mục lỗi thường gặp) và file Excel của môn:
- *Đúng:* lề 3,5/2/3/3,5 cm; Times New Roman 13; giãn 1,5 dòng (cả danh mục tài liệu); thụt đầu dòng 1 tab, căn đều; số trang giữa phía trên; tiểu mục tối đa 3 cấp, nhóm nào cũng ≥ 2 tiểu mục; tiêu đề dính đoạn sau; số hình/bảng gắn số chương, chú thích bảng trên, hình dưới, mọi Hình/Bảng được nhắc theo số trong thân bài; hàng tiêu đề bảng lặp khi sang trang; danh mục viết tắt xếp ABC, không bẻ dòng; danh mục tài liệu chia A. Văn bản quy phạm pháp luật (5 luật, "Tên (Luật số …) ngày …", có test đối chiếu `data/raw/laws.json`) và B. Tài liệu tham khảo (APA, đều tiếng Anh nên không chia nhóm ngôn ngữ, Đạt quyết 16/11); lời cảm ơn ghi "PGS.TS."; có nội dung sheet yêu cầu: quản lý dự án (cuối 1.4), ý nghĩa khoa học và thực tiễn (1.6), khả năng ứng dụng thực tế (5.7).
- *Còn kiểm trên bản PDF cuối:* khoảng trống lớn giữa trang (lỗi thường gặp).

**Kiểm bằng ảnh:** `bash docs/managements/tools/topdf.sh "$PWD/docs/report/final_52300098_52300106.docx" <scratchpad>/r.pdf` rồi `pdftoppm` (trong zsh, `rm` với glob không khớp sẽ lỗi và dừng chuỗi `&&`; lệnh `rm -f *` sau `cd` bị Claude Code chặn, dùng thư mục mới trống thay vì xóa). `topdf.sh` đang hỏng, xem mục 2 việc 1.

**Yêu cầu của môn** (sheet "Thông tin môn học_DỰ ÁN" và "Rubric" trong `docs/report/HƯỚNG DẪN BÁO CÁO/Copy of QL. DỰ ÁN CNTT_ĐATN _KLTN.xlsx`, đọc đủ 16/11 bằng zipfile + ElementTree): môn Dự án CNTT (504091), 3 tín chỉ; điểm = 40% GK + 60% CK, CK = (HD + PB1 + PB2)/3; **nộp ELIT `MSSV1_MSSV2.zip`** (nội dung ở mục 2 việc 6) trước 1 tuần so với ngày công bố hội đồng phản biện, nộp trễ thì không được sửa hình thức, đạo văn; khoa kiểm đạo văn và thể thức; 2 GV phản biện độc lập, báo cáo trực tiếp, mang quyển báo cáo; thuyết trình 15 phút, trao đổi 30 phút. *Lưu ý nội dung* (ô B19): xác định vấn đề, giải pháp có phương pháp luận, thực hiện, đánh giá (có **sẵn sàng ứng dụng thực tế**), **công cụ quản lý dự án**. *Rubric:* trừ điểm (sai tên GV/SV/khoa −1; lỗi diễn đạt, định dạng −1…+1; bố cục −1…+1; template sai −1; thiếu trích dẫn −1…+1; đạo văn > 20% từ −2) và 10 điểm chính: hiểu đề tài 5 (lý do, ý nghĩa 1; lý thuyết, khảo sát 2; code, xử lý dữ liệu 2), kết quả 5 (hàm lượng khoa học 2; chứng minh độ tin cậy 2; tính mới 1).

**Slide bảo vệ (H24, xong 16/11):** `docs/defense/build_slides.js` → `docs/defense/Slide bảo vệ - ĐA127.pptx`, 17 slide theo dàn ý thẻ H24, cùng thiết kế slide báo cáo tuần, mỗi slide có lời thuyết trình (script in tổng số từ, khoảng 12 phút ở 130 từ/phút). Mọi số lấy từ Chương 5, 6; slide RQ4 dùng câu trả lời thật của M_016 (`eval/results/agent_rq4.jsonl`: event trích BLLĐ 2012 Điều 22, current trích BLLĐ 2019 Điều 20). Đạt đã duyệt.

## 6. Nhật ký các phiên từ 19/11 (cho báo cáo tuần 15)

Chưa có nhật ký: các việc 16/11 và 18–19/11 đã nằm trong báo cáo tuần 14 (`docs/managements/Week 16.11-22.11/`), phiên sau bắt đầu ghi từ đây. Mỗi phiên ghi: commit, việc đã làm, số liệu, khó khăn + tình trạng (Đã xử lý / Giảm thiểu / Chấp nhận, ghi vào giới hạn / Đang theo dõi), tiến độ PLAN (hiện 75/79, 95%).

**Khó khăn còn mở, mang sang tuần 15** (các mục đã xử lý nằm trong ch4 của báo cáo tuần 14):
- Không có Word; OnlyOffice là công cụ duy nhất để xem: **Giảm thiểu** (trang trắng, khoảng trống giữa trang chỉ kiểm được trên bản PDF cuối).
- Docker chưa kiểm trên máy sạch, Windows: **Đang theo dõi** (chạy tốt trên máy Đạt).
- Gemini 503: **Giảm thiểu** (ảnh hưởng quay video demo).
- Bản PDF QĐ 2284 là ảnh scan: **Giảm thiểu** (dùng bản hướng dẫn .docx đi kèm).
- Giới hạn thực nghiệm (prompt chỉnh trên tập kiểm thử, bộ chấm, cỡ mẫu): **Chấp nhận, đã ghi vào giới hạn**.
- Hủy làm lại giao diện (tuần 13): **Chấp nhận**.
- `topdf.sh` hỏng do bộ đệm font OnlyOffice (phát hiện 19/11): **Đang theo dõi** (mục 2 việc 1).

## 7. Công cụ và ghi chú

- **Báo cáo tuần:** `docs/managements/tools/README.md` (có đoạn tuần 14 và đoạn về bộ đệm font). Mỗi tuần một thư mục `Week <dd.mm-dd.mm>/` có `content.json`, `build_pptx.js`, `build_xlsx.py` riêng; `build_docx.py` dùng chung. Mẫu docx KLTN ở repo `vn-legal-verify` (`~/0. Ton_Duc_Thang_University/HK7/Graduation_Thesis/vn-legal-verify/docs/managements/Mid_Term/`). Môi trường tạm: venv có `python-docx`, `openpyxl`; `npm install pptxgenjs@3.12.0` trong một thư mục tạm rồi `NODE_PATH=<dir>/node_modules`. Mẫu Excel KLTN phải lấy bản `2a13ff0` (README đã ghi cách lấy).
- **Slide bảo vệ:** `NODE_PATH=<dir>/node_modules node docs/defense/build_slides.js "docs/defense/Slide bảo vệ - ĐA127.pptx"` (chạy từ gốc repo; ảnh lấy từ `assets/`, `docs/report/figures/`, logo `docs/managements/tools/logo.png`); xem trước: `topdf.sh` file pptx rồi `pdftoppm`.
- **Sơ đồ draw.io:** `assets/diagrams/*.drawio` (architecture, agent_graph, usecase, sequence, activity, 4 hình Chương 3). Xuất PNG từ terminal VSCode phải bỏ biến `ELECTRON_RUN_AS_NODE`: `env -u ELECTRON_RUN_AS_NODE drawio -x -f png -s 2 -b 10 -o X.png X.drawio`. Ảnh cũ do AI vẽ (`architecture_old.png`, `agent_graph_old.png`) sai so với code, không dùng.
- **Hình Chương 3:** `python3 IT_Project/tools/ch3_figures.py <thư mục ra>` (ngoài git, dùng lại `styled.py` của Hình 4.1–4.2) sinh 4 file `.drawio`, xuất PNG bằng lệnh drawio ở trên, chép `.drawio` và `.png` vào `assets/diagrams/`. `activity.drawio` sửa trực tiếp trong draw.io.
- `IT_Project/tools/ui_shot.js` (ngoài git) chụp giao diện hoặc trang HTML bằng Electron: `env -u ELECTRON_RUN_AS_NODE electron44 ../tools/ui_shot.js <url> OUT.png 1440 900 "ask:<câu hỏi>" "click:<chữ đầu của phần tử>" "wait:<ms>"`.
- Chạy giao diện không tốn quota (phát lại kết quả đã chạy): `LLM_API_KEY= UI_LOCAL_FALLBACK=1 API_URL=http://127.0.0.1:8999 .venv/bin/python -m src.ui.web.main`; tắt: `pkill -f '[s]rc\.ui\.web\.main'`.
- Thư mục hướng dẫn và mẫu của khoa chuyển từ `docs/managements/` sang `docs/report/HƯỚNG DẪN BÁO CÁO/` (19/11); `build_report.py` đọc mẫu ở đó. `graphify-out/` (đồ thị tri thức của repo, sinh 18/11) nằm ở `IT_Project/graphify-out/`, ngoài git.
- Skill trong project (`IT_Project/.claude/skills/`): chỉ còn Impeccable (có hook trong `IT_Project/.claude/settings.local.json`, chạy sau mỗi lần sửa file khi mở phiên ở `IT_Project/`). Không dùng `live-server`/`live-inject` của nó (sửa file của dự án). Skill Taste và diagram-design đã gỡ 16/11.
