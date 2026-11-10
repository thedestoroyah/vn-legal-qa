# Bàn giao phiên làm việc (cập nhật 11/11/2026)

> Nhật ký của Đạt, **track trong git từ 10/11** (trước đó bị gitignore). Bối cảnh ít đổi (đề tài, kiến trúc, quy tắc tập kiểm thử, lệnh): `AGENTS.md`. Claude Code tự nạp cả hai qua `IT_Project/CLAUDE.md` (thư mục cha, ngoài git), dù mở phiên ở `IT_Project/` hay `vn-legal-qa/`.
>
> Trước 10/11 file nằm ngoài git nên từng bị khôi phục về bản cũ (05/11, do rollback phiên). Từ 10/11 có lịch sử trong git: nếu ngày cập nhật ở trên cũ hơn `git log`, xem `git log -p -- docs/HANDOFF.md` trước khi tin file.

## 1. Trạng thái

**Git:** phiên 10/11 có 8 commit tài liệu trên `main` (`dc951b0` → commit plan H22, xem mục 6) + các commit 11/11: vá lỗi giao diện (H22 đã hủy, mục 6) và H23 ghép báo cáo (mục 7); Đạt push. Tag chỉ ở máy Đạt, chưa push: `ui-before-h22` (giao diện trước mọi sửa đổi), `h22-attempt` (bản H22 đầy đủ đã làm rồi bỏ: 12 commit, 353 test, review độc lập). Test: 363 pass. HANDOFF được track trong git từ 10/11.

**Sprint 5 (05/11–15/11):** phần của Đạt xong hết (Task 1–7, phân tích lỗi, latency, kiểm giao diện H19). Sổ quyết định: `.superpowers/sdd/2026-11-05-sprint5-dat/progress.md`. **10/11: Đạt làm thay H17, H18, H21** (Hùng không cập nhật gì từ 06/11); sổ quyết định `.superpowers/sdd/2026-11-05-sprint5-hung/progress.md`.

**Sprint 6 (16/11–27/11, làm sớm được vì không phải tính năng mới):** plan đã được Đạt duyệt: `docs/superpowers/plans/2026-11-16-sprint6-dat.md`; thẻ Hùng `docs/sprints/2026-11-16-sprint6-hung.md` (H22 giao diện, H23 ghép báo cáo, H24 slide bảo vệ, H25 video demo). Chạy 06/11 theo `superpowers:executing-plans`: **Task 1, 3, 4 xong, đã commit và push; Task 2 chạy được, chỉ còn Đạt mở giao diện bằng trình duyệt một lần.** Đã qua review độc lập cuối; các lỗi Important và Minor của Sprint 6 đã sửa, trừ 2 mục giao diện ở H22 (mục 7–8). Image `vn-legal-qa` 3,23 GB đã build trên máy Đạt. Task 5 chờ Hùng ghép báo cáo (H23, hạn 24/11). Tiến độ và mọi quyết định: `.superpowers/sdd/2026-11-16-sprint6-dat/progress.md`.

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

1. **H22 đã hủy (10/11, mục 6).** Không làm lại giao diện, không làm web riêng (trái mốc đóng băng, không thêm số liệu cho báo cáo). Còn treo: mục 8 thẻ H22 (gợi ý "đợi vài giây rồi bấm Thử lại" sai với lỗi 500), sửa nhỏ ở `src/ui/web/api/client.py` nếu muốn.
2. **Task 2 Sprint 6:** Đạt mở giao diện qua `docker compose up --build` một lần (phải `--build`: image trên máy đang chứa giao diện H22 đã hủy), xác nhận thanh bên ghi "Đã kết nối · gemini-3.1-flash-lite", đánh dấu Task 2 ở `PLAN.md` và Phụ lục B.
3. **Báo cáo tuần 13 (09.11–15.11, khoảng 13/11):** nội dung = mục 5 (việc 06/11) + mục 6 "Nhật ký phiên 10/11" (gồm H22: đánh giá, thử, hủy, vá 2 lỗi). Prompt ở mục 4.
4. **Báo cáo docx (H23, Đạt làm thay, mục 7):** mở `docs/report/final_52300098_52300106.docx` bằng Word hoặc OnlyOffice, đồng ý cập nhật trường (file tự hỏi khi mở) để mục lục, danh mục hình, danh mục bảng có số trang; xem nhanh trước khi rà soát. **Task 5 Sprint 6 (rà soát, Turnitin) làm được ngay**, không chờ 24/11: sửa lỗi ở file `.md` rồi `python docs/report/build_report.py`.
5. **Theo dõi Hùng** (không cập nhật gì từ 06/11): gửi tin nhắn mới (bản nháp trong phiên 11/11: H23 Đạt đã làm, Hùng chỉ còn H26, H24, H25). H26: 4 hình lưu đúng tên `assets/diagrams/bi_encoder.png`, `cross_encoder.png`, `naive_rag.png`, `agentic_rag.png`, bỏ Hình 3.5 khỏi `chuong3_draft.md` (hạn 20/11); build sẽ hết 5 cảnh báo "thiếu ảnh". H26 phần activity: sửa xong `activity.drawio`/`.png` thì Đạt thêm comment `<!-- Hình 4.8: assets/diagrams/activity.png -->` + chú thích vào Chương 4 rồi build lại. Khoảng 20/11 vẫn im lặng thì Đạt nhận H24 (slide).
6. Tùy chọn: gỡ skill Taste (không hợp NiceGUI, Claude Code không đọc thư mục `.agents/`): `rm -rf IT_Project/.agents/skills/design-taste-frontend`; tắt gửi số liệu ẩn danh của Impeccable: `IT_Project/.claude/skills/impeccable/scripts/impeccable telemetry off`; cài Chromium (`sudo pacman -S chromium`) nếu muốn bộ phát hiện quét URL trực tiếp.

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
- **Tài liệu tham khảo đã tra 03/11** (arXiv API, ACL Anthology, Crossref, NeurIPS, bản PDF của tác giả): 13 mục mục 12 đề cương + Lewis 2020. Sửa: BGE-M3 → tên mới + Findings ACL 2024, 2318–2335; Reuter thêm trang 17–30; RAGAS 'Espinosa Anke'; thêm DOI. BM25 giữ 3(4) 333–389 (trang nhà xuất bản/Crossref ghi 4(1-2) 1–174 là sai). CRAG chỉ có bản arXiv. Chương 1 hết `[CẦN KIỂM TRA]`. Chưa làm: chuyển danh mục sang đúng định dạng mẫu khoa khi ghép docx (H23).

## 4. Gợi ý prompt cho phiên mới

**Chạy H22 (giao diện)**
```
Chạy plan docs/superpowers/plans/2026-11-10-h22-ui-dat.md theo superpowers:executing-plans (native); mỗi task dùng skill impeccable với lệnh ghi trong plan. Đọc HANDOFF mục 6 "Công cụ" trước. Rollback: tag ui-before-h22. Commit theo plan, không push.
```


**Tiếp tục chung**
```
Tóm tắt trạng thái hiện tại và 3 việc nên làm tiếp. Chưa làm gì, chưa commit.
```

**Chạy Task 5 Sprint 6 (sau khi Hùng gửi docx H23)**
```
Chạy Task 5 của plan docs/superpowers/plans/2026-11-16-sprint6-dat.md (rà soát báo cáo), đọc ledger .superpowers/sdd/2026-11-16-sprint6-dat/progress.md trước. Turnitin tôi tự nộp. Không commit, báo tôi khi xong.
```

**Pull việc của Hùng**
```
Repo có cập nhật, pull về (theo CLAUDE.md), kiểm tra Hùng sửa gì, chạy test, báo xung đột với AGENTS.md (nhất là tập kiểm thử, prompt) rồi làm tiếp.
```

**Báo cáo tuần mới**
```
Đọc docs/managements/tools/README.md và docs/HANDOFF.md mục 5, 6. Làm báo cáo tuần 13 (09.11-15.11) trong docs/managements/Week 09.11-15.11: chép content.json, build_pptx.js, build_xlsx.py của tuần 12 rồi sửa; cùng 4 chương, cùng thiết kế. Tính cả việc làm ngày 06/11 ghi ở mục 5, thêm việc phát sinh từ 07/11 lấy từ git log (cả của Hùng). Khó khăn tuần 12 đã xong thì chuyển sang ch4.resolved, còn lại giữ nhãn tình trạng. Kiểm bằng ảnh render.
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

**Kế hoạch phần còn lại trong báo cáo:** Sprint 6 của Đạt chỉ còn Task 5 (rà soát báo cáo, Turnitin) sau H23; việc còn lại của Hùng: H17, H18, H21, H22, H23, H24, H25.

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

**Cách làm:** script `docs/report/build_report.py` (thư viện chuẩn + `pandoc`, không thêm dependency): tiền xử lý 6 chương (bỏ ghi chú nháp, comment nguồn, số tiêu đề gõ tay; comment hình thành ảnh) → pandoc với khung làm reference → đổi style sang style khung (`Nidungvnbn`, `Caption`, `TableGrid`, `Bibliography`) → ghép vào `docs/report/khung_TDTU.docx`. Lệnh: `python docs/report/build_report.py` (`--strict` thoát mã 1 nếu còn cảnh báo). Kết quả `docs/report/final_52300098_52300106.docx`, khoảng 75 trang. 21 test trong `tests/test_build_report.py`. Ảnh: rộng tối đa 15 cm, giữ ≥ 150 dpi, cao ≤ 20 cm. Mục lục và hai danh mục trong file là dòng nhắc "Chưa cập nhật… F9" cho tới khi cập nhật trường.

**Theo mẫu khoa `docs/managements/Template_VN.dotx`** (Đạt đưa 10/11, đã commit): chú thích "Hình 4.1: …"/"Bảng 5.1: …" có trường `STYLEREF 1 \s` + `SEQ Hình \s 1` (danh mục hình, bảng tự cập nhật); bảng có chú thích ở trên, hình ở dưới; tài liệu tham khảo APA 7, thụt treo 0,5", tên nguồn in nghiêng.

**Sửa so với khung của Hùng:** danh mục hình/bảng luôn rỗng (chú thích dùng mã "Hình_2." thay vì "Hình"); tài liệu tham khảo kiểu IEEE [1]… trong khi thân bài trích tác giả–năm → thay bằng 15 mục mục 12 đề cương (APA 7, có kiểm tự động trích dẫn ↔ danh mục); tiêu đề tiếng Anh khác đề cương → đúng nguyên văn mục 1; Tóm tắt, Abstract còn chữ mẫu → viết mới khoảng 200 từ mỗi bản từ số liệu Chương 6 (`docs/report/phan_dau.md`); bảng viết tắt trống → 20 từ có thật trong 6 chương; lời cảm ơn lặp chữ; cam đoan đổi "tôi" thành "chúng tôi" (Đạt quyết định). Chương mới sang trang, bảng rộng hết trang.

**Nguồn Markdown đã sửa:** Chương 4 tách chú thích gộp "Hình 4.3–4.5", "Hình 4.6–4.7" thành từng hình; Chương 3 bỏ nhãn `[CẦN KIỂM TRA]` cạnh Lewis (2020) (tài liệu đã có ở mục 12).

**Review độc lập (Opus):** 0 Critical, 3 Important, đã sửa có test: Hình 4.7 quá nhỏ, mục lục lưu sẵn của khung cũ, id ảnh pandoc không được đánh lại (sẽ trùng khi H26 thêm hình), tiêu đề cấp 4 Chương 3 lặp số. Không đưa `activity.png` vào báo cáo vì đang lệch code 7 điểm (H26). 10 lỗi nhỏ hoãn: dòng `Final: minor` trong sổ quyết định (đáng làm khi rảnh: thứ tự APA Nguyen, T.-M. trước Nguyen Ba; thêm ALCE, AI, JSONL vào bảng viết tắt; Chương 3 có danh sách viết liền trong đoạn).

**Còn lại:** 5 cảnh báo "thiếu ảnh" Hình 3.1–3.5 (chờ H26; hiện ô "[CHỜ HÌNH 3.x: …]" trong file); mở bằng Word/OnlyOffice cập nhật trường; trang ký (ngày, chữ ký) làm tay ở bản nộp.

**Khó khăn (cho chương 4 báo cáo tuần 13):** Hùng không phản hồi, H23 hạn 24/11 chặn rà soát và Turnitin → Đạt làm bằng script, Markdown là nguồn duy nhất, build lại trong vài giây. *Đã xử lý.* Khung docx có lỗi định dạng ẩn (danh mục hình rỗng, kiểu trích dẫn lệch) → phát hiện khi đối chiếu với mẫu khoa. *Đã xử lý.*
