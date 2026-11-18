# CHƯƠNG 5. THỰC NGHIỆM VÀ ĐÁNH GIÁ

> **Bản nháp Task 7 Sprint 5** — Đạt, 03/11/2026. Mọi số liệu lấy từ `eval/results/`; mỗi bảng ghi file nguồn trong comment.
> Số thập phân trong file nguồn dùng dấu chấm; khi chép sang báo cáo đổi thành dấu phẩy.

## 5.1. Thiết lập thực nghiệm

### 5.1.1. Tập kiểm thử

Tập kiểm thử gồm 209 câu hỏi từ ba nguồn (Bảng 5.1). Kết quả luôn báo cáo tách theo nguồn vì mỗi nguồn một khác. Câu Zalo là câu hỏi thực tế của người dân, chỉ có căn cứ chuẩn ở cấp Điều và không có đáp án mẫu. Câu tổng hợp sinh từ chính văn bản trong kho nên dễ hơn. Câu tự soạn xoáy vào các tình huống hệ thống được thiết kế để xử lý (mốc thời gian, tra cứu trực tiếp, ngoài phạm vi).

**Bảng 5.1.** Thành phần tập kiểm thử.
<!-- nguồn: eval/test_cases.json (sinh bằng python -m eval.import_cases) -->

| Nguồn | Tình huống | Có mốc thời gian | Tra cứu trực tiếp | Ngoài phạm vi | Tổng | Có đáp án mẫu |
|---|---|---|---|---|---|---|
| Zalo AI Legal Text Retrieval (lọc theo 5 văn bản trong kho) | 77 | – | – | – | 77 | không |
| Tổng hợp (sinh bằng LLM từ văn bản; kiểm tay mẫu 20 câu, đạt 20/20) | 65 | – | – | – | 65 | có |
| Tự soạn (nhóm) | 15 | 32 | 15 | 5 | 67 | có |
| Tổng | 157 | 32 | 15 | 5 | 209 | 132 câu |

Tập giữ riêng gồm 30 câu tự soạn (M_038–M_067), trong đó 20 câu có mốc thời gian theo 10 cặp quy định khác nhau giữa BLLĐ 2012 và BLLĐ 2019, 10 câu tra cứu trực tiếp. Nhóm soạn và chốt 30 câu này sau khi prompt đã cố định, trước khi chạy hệ thống trên câu nào trong số đó (`docs/superpowers/specs/2026-11-03-heldout-prereg.md`). Văn bản chốt trước ghi rõ giả thuyết, cách phân tích và cam kết báo cáo kết quả kể cả khi giả thuyết không được ủng hộ. Tập này nhằm giảm giới hạn "prompt được chỉnh sau khi thấy lỗi trên tập kiểm thử" (mục 5.7). Mô hình ngôn ngữ soạn nháp các câu từ văn bản luật trong kho, thành viên nhóm kiểm và sửa từng câu.

### 5.1.2. Chỉ số

- Chỉ số truy xuất (RQ1, RQ2), tính ở cấp Điều: Hit@5 (có ít nhất một Điều chuẩn trong 5 kết quả đầu), Recall@10 (tỷ lệ Điều chuẩn có trong 10 kết quả đầu), MRR@10. Riêng RQ2 đo thêm DRM@5: tỷ lệ đoạn trong 5 kết quả đầu thuộc văn bản không có trong căn cứ chuẩn (nhầm văn bản, mục 2.1.2).
- Chỉ số trích dẫn (RQ3, RQ4), tính ở cấp Điều: Citation Precision (tỷ lệ Điều được trích thuộc căn cứ chuẩn, chỉ tính câu có trích dẫn) và Citation Recall (tỷ lệ Điều chuẩn được trích).
- Từ chối đúng: câu ngoài phạm vi phải bị từ chối, câu trong phạm vi phải được trả lời.
- Đúng phiên bản (chỉ câu có mốc thời gian): mọi văn bản luật lao động được trích đều là phiên bản có hiệu lực tại ngày sự việc.
- Faithfulness và Answer Correctness (thang 0 / 0,5 / 1) do mô hình `openai/gpt-oss-120b` qua Groq chấm, khác nhà cung cấp với mô hình của tác tử, mỗi câu trả lời một lượt. Bộ chấm chỉ chấm câu được trả lời, riêng Correctness chỉ chấm câu có đáp án mẫu.

### 5.1.3. Kiểm định thống kê

Các cấu hình được so sánh ghép cặp theo câu. Mỗi câu có giá trị ở cả hai cấu hình thì lấy hiệu số, rồi ước lượng khoảng tin cậy 95% của trung bình hiệu số bằng bootstrap 2.000 lần lấy mẫu lại theo câu (seed cố định). Chênh lệch có ý nghĩa (ký hiệu `*`) khi khoảng tin cậy không chứa 0.

### 5.1.4. Kiểm định bộ chấm

Một thành viên chấm tay độc lập 20 câu trả lời của cấu hình `full` theo thang ở `docs/rubric.md`, rồi so với bộ chấm. Tỷ lệ khớp là 0,950 với Faithfulness (20 câu) và 0,917 với Correctness (12 câu có đáp án mẫu). Tuy vậy, bộ chấm cho điểm 1 ở mọi câu trong mẫu nên hệ số kappa bằng 0. Tỷ lệ khớp cao chủ yếu do phần lớn câu trả lời đúng thật (người chấm cho 19/20 và 11/12 câu điểm 1), chưa chứng minh được bộ chấm phân biệt được câu sai. Hai câu lệch đều do người chấm chặt hơn bộ chấm. Do đó chương này dựa chủ yếu vào các chỉ số tính bằng code (trích dẫn, phiên bản, từ chối), Faithfulness và Correctness chỉ là chỉ số bổ trợ.
<!-- nguồn: eval/results/grading_rq3_dat.csv; python -m eval.agent_eval agree --rq rq3 --filled eval/results/grading_rq3_dat.csv -->

## 5.2. RQ1: Phương pháp truy xuất

**Bảng 5.2.** Kết quả truy xuất trên 77 câu Zalo (biến thể Khoản + tiêu đề).
<!-- nguồn: eval/results/retrieval_rq1.md (dòng source = zalo) -->

| Phương pháp | Hit@5 | Recall@10 | MRR@10 | Thời gian/câu (ms) |
|---|---|---|---|---|
| BM25 | 0,766 | 0,810 | 0,717 | 13 |
| Dense (BGE-M3) | 0,844 | 0,872 | 0,748 | 235 |
| Hybrid (RRF) | 0,805 | 0,872 | 0,741 | 148 |
| Hybrid + rerank | 0,844 | 0,872 | 0,807 | 6.805 |

<!-- Hình 5.1: docs/report/figures/rq1.png -->
**Hình 5.1.** Hit@5 và Recall@10 theo phương pháp truy xuất.

Theo Bảng 5.2 và Hình 5.1, Hybrid + rerank đạt cả hai chỉ tiêu đề ra (Hit@5 ≥ 0,80, Recall@10 ≥ 0,75). Có ba nhận xét:

- Dense hơn hẳn BM25 trên câu Zalo (Hit@5 0,844 so với 0,766) vì câu hỏi đời thường ít trùng từ với văn bản luật.
- Hợp nhất RRF không làm Hit@5 tốt hơn Dense (0,805 so với 0,844), có thể vì nhánh BM25 yếu hơn kéo một số Điều sai lên top 5. Sau khi rerank, MRR@10 tăng từ 0,748 lên 0,807, tức Điều đúng lên vị trí cao hơn, có ích vì tác tử chỉ đọc 5 đoạn đầu.
- Đổi lại, rerank trên CPU tăng thời gian truy xuất từ dưới 0,25 giây lên khoảng 6,8 giây mỗi câu.

Trên 157 câu có căn cứ chuẩn (gồm cả câu tổng hợp và câu tự soạn), Hybrid + rerank đạt Hit@5 0,924 và Recall@10 0,937.

## 5.3. RQ2: Cách phân đoạn

**Bảng 5.3.** Kết quả theo cách phân đoạn trên 77 câu Zalo (Hybrid + rerank).
<!-- nguồn: eval/results/retrieval_rq2.md (dòng source = zalo) -->

| Phân đoạn | Hit@5 | Recall@10 | MRR@10 | DRM@5 (thấp hơn là tốt hơn) |
|---|---|---|---|---|
| Cố định 200 từ | 0,597 | 0,617 | 0,516 | 0,083 |
| Điều (kèm tiêu đề) | 0,883 | 0,890 | 0,825 | 0,099 |
| Khoản (chỉ nội dung) | 0,857 | 0,872 | 0,806 | 0,101 |
| Khoản + tiêu đề | 0,844 | 0,872 | 0,807 | 0,075 |

<!-- Hình 5.2: docs/report/figures/rq2.png -->
**Hình 5.2.** Hit@5 và Recall@10 theo cách phân đoạn.

Bảng 5.3 và Hình 5.2 cho thấy phân đoạn theo cấu trúc luật hơn hẳn cắt cố định (Hit@5 cao hơn 0,25–0,29), vì cửa sổ cố định cắt ngang Điều và trộn nội dung của nhiều Điều. Trong ba cách theo cấu trúc, cấp Điều cho kết quả cao nhất trên câu Zalo, cũng dễ hiểu vì căn cứ chuẩn của Zalo ở cấp Điều. Hệ thống vẫn lấy cấp Khoản làm mặc định vì trích dẫn tới Khoản cụ thể hơn cho người đọc, và trên 157 câu có căn cứ chuẩn, Khoản + tiêu đề đạt Hit@5 0,924, bằng cấp Điều. Gắn tiêu đề phân cấp không tạo khác biệt trên câu Zalo (0,844 so với 0,857) nhưng nâng Hit@5 trên câu tổng hợp từ 0,908 lên 1,000.

Về nhầm văn bản, DRM@5 của cả bốn cách đều thấp, từ 0,075 đến 0,101 trên câu Zalo; Khoản + tiêu đề thấp nhất (0,075, so với 0,101 của Khoản chỉ nội dung; trên 157 câu là 0,075 so với 0,098). Chênh lệch này nhỏ, chưa kiểm định thống kê và chưa đủ để quy riêng cho tiêu đề. Phân đoạn cấp Điều cũng có tiêu đề mà DRM@5 vẫn là 0,099, và đoạn của mỗi cách dài ngắn khác nhau nên năm đoạn đầu không tương đương. Các câu của RQ2 không nêu thời điểm sự việc nên truy xuất chỉ chạy trên 4 văn bản còn hiệu lực. DRM@5 ở đây đo nhầm giữa các văn bản khác lĩnh vực, còn nhầm giữa hai phiên bản Bộ luật Lao động đo bằng tỷ lệ đúng phiên bản ở RQ3 và RQ4. Cắt cố định có DRM@5 thấp (0,083) dù Hit@5 kém nhất, vì DRM@5 chỉ tính đoạn lấy nhầm văn bản, đoạn đúng văn bản mà sai Điều thì không tính.

## 5.4. RQ3: Đóng góp của các thành phần tác tử

### 5.4.1. Kết quả trên toàn bộ 209 câu

**Bảng 5.4.** Năm cấu hình trên 209 câu.
<!-- nguồn: eval/results/agent_rq3_ablation209.md (dòng source = all) -->

| Cấu hình | Trả lời | Cit. P | Cit. R | Từ chối đúng | Đúng phiên bản (32) | Faithful­ness | Correct­ness (132) | LLM/câu |
|---|---|---|---|---|---|---|---|---|
| baseline | 0,895 | 0,795 | 0,810 | 0,919 | 0,500 | 0,995 | 0,826 | 1,0 |
| full | 0,871 | 0,870 | 0,825 | 0,895 | 0,750 | 0,992 | 0,871 | 4,0 |
| no_router | 0,876 | 0,833 | 0,791 | 0,900 | 0,500 | 0,989 | 0,830 | 3,2 |
| no_grading | 0,861 | 0,868 | 0,810 | 0,885 | 0,750 | 0,992 | 0,871 | 3,0 |
| no_verify | 0,871 | 0,859 | 0,859 | 0,895 | 0,750 | 0,992 | 0,867 | 3,0 |

**Bảng 5.5.** Chênh lệch so với `full`, ghép cặp theo câu, khoảng tin cậy bootstrap 95%.
<!-- nguồn: eval/results/agent_rq3_ablation209.md (bảng chênh lệch) -->

| Cấu hình | Cit. P | Cit. R | Đúng phiên bản | Correctness |
|---|---|---|---|---|
| baseline | −0,060* [−0,097; −0,024] | −0,015 [−0,069; 0,044] | −0,250* [−0,469; −0,062] | −0,045 [−0,102; 0,008] |
| no_router | −0,021 [−0,047; 0,000] | −0,034 [−0,069; 0,000] | −0,250* [−0,438; −0,062] | −0,042 [−0,083; 0,000] |
| no_grading | −0,005 [−0,013; 0,000] | −0,015 [−0,049; 0,025] | 0,000 [−0,094; 0,094] | 0,000 [−0,030; 0,030] |
| no_verify | −0,016* [−0,033; −0,002] | +0,034* [0,015; 0,064] | 0,000 | −0,004 [−0,023; 0,011] |

<!-- Hình 5.3: docs/report/figures/rq3_diff.png -->
**Hình 5.3.** Chênh lệch so với `full` và khoảng tin cậy 95% (chấm đặc: có ý nghĩa).

`full` đạt chỉ tiêu Citation Precision ≥ 0,85 (0,870). Hình 5.3 biểu diễn các chênh lệch của Bảng 5.5. Xét từng thành phần:

- Bỏ router thì tỷ lệ đúng phiên bản giảm 0,250 (có ý nghĩa). Không có router thì không có ngày sự việc, truy xuất chỉ lấy văn bản còn hiệu lực, nên câu về sự việc trước năm 2021 bị trả lời theo BLLĐ 2019 hoặc bị từ chối. Citation Recall và Correctness cũng giảm (−0,034 và −0,042), cùng chiều nhưng khoảng tin cậy chạm 0.
- Bước grade (viết lại truy vấn) ở `full` yêu cầu viết lại truy vấn ở 27/209 câu, nhưng so với `no_grading` thì không chỉ số nào khác biệt đo được, trong khi tốn thêm khoảng 1 lượt LLM mỗi câu.
- Bỏ verify (b) thì Citation Recall tăng 0,034 còn Citation Precision giảm 0,016, cả hai đều có ý nghĩa. Verify (b) gỡ một số trích dẫn đúng (giảm recall) để loại được trích dẫn không hỗ trợ (tăng precision). Trên dữ liệu kiểm thử tự nhiên, mô hình ít khi trích sai nên khó thấy lợi ích của verify; mục 5.4.3 đo trực tiếp khả năng bắt trích dẫn sai.
- `baseline` (RAG một lượt, không router, grade, verify (b)) kém `full` rõ nhất ở Citation Precision (−0,060\*) và đúng phiên bản (−0,250\*), bù lại chỉ tốn 1 lượt LLM mỗi câu so với khoảng 4.

### 5.4.2. Tập giữ riêng (30 câu)

**Bảng 5.6.** Năm cấu hình trên 30 câu giữ riêng (20 câu có mốc thời gian, 10 câu tra cứu trực tiếp).
<!-- nguồn: eval/results/agent_rq3_heldout30.md -->

| Cấu hình | Trả lời | Cit. P | Cit. R | Đúng phiên bản (20) | Correctness |
|---|---|---|---|---|---|
| baseline | 0,967 | 0,638 | 0,633 | 0,500 | 0,667 |
| full | 0,767 | 0,978 | 0,767 | 0,700 | 0,750 |
| no_router | 0,833 | 0,740 | 0,633 | 0,500 | 0,667 |
| no_grading | 0,767 | 0,978 | 0,767 | 0,700 | 0,750 |
| no_verify | 0,767 | 0,957 | 0,767 | 0,700 | 0,750 |

Giả thuyết chốt trước H1 là `no_router` kém `full` về Correctness và đúng phiên bản trên loại câu này. Trên 30 câu (Bảng 5.6), mọi chỉ số của `no_router` đều thấp hơn `full` (Cit. P −0,143, Cit. R −0,133, đúng phiên bản −0,200, Correctness −0,083) nhưng chưa có chênh lệch nào có ý nghĩa (cận trên của khoảng tin cậy chạm hoặc vượt 0). Gộp với tập cũ (Bảng 5.5), chênh lệch đúng phiên bản có ý nghĩa. H1 vì vậy được ủng hộ ở chỉ số đúng phiên bản. Với Correctness, xu hướng cùng chiều nhưng cỡ mẫu chưa đủ để khẳng định.

`full` trả lời 23/30 câu, ít hơn `no_router` (25/30) và `baseline` (29/30). Cả 30 câu đều trong phạm vi, nên lần từ chối nào cũng là từ chối nhầm. Trong 7 lần `full` từ chối, 6 lần do bước grade hoặc generate kết luận căn cứ không đủ (4 lần sau khi đã viết lại truy vấn tới mức tối đa), 1 lần (M_051) do router xếp nhầm câu hỏi là ngoài phạm vi. Riêng M_066 hỏi thẳng một Điều của BLLĐ 2012 (đã hết hiệu lực) mà không nêu ngày sự việc, nên Điều đó bị lọc theo văn bản còn hiệu lực rồi bị từ chối. `full` thận trọng hơn: thiếu căn cứ đúng phiên bản thì từ chối, còn `no_router` trả lời bằng văn bản sai phiên bản. Đây là đánh đổi giữa độ phủ và độ chính xác (Cit. P 0,978 so với 0,740), mục 5.6 phân tích thêm.

### 5.4.3. Phép thử tiêm trích dẫn sai

Tập kiểm thử tự nhiên ít có trích dẫn sai, nên nhóm đo trực tiếp khả năng của verify (b). Cách làm là lấy câu trả lời của `full`, thay một mã trích dẫn trong một câu bằng một đoạn "mồi" không hỗ trợ câu đó, đưa đoạn mồi vào ngữ cảnh (để verify (a) không bắt được), rồi chạy verify (b) một lượt.

**Bảng 5.7.** Kết quả phép thử tiêm trích dẫn sai.
<!-- nguồn: eval/results/verify_attack.md -->

| Loại mồi | Số lần thử | Mồi bị gỡ | Mã đúng bị gỡ nhầm |
|---|---|---|---|
| Đoạn đã truy xuất nhưng khác Điều (cùng ngữ cảnh) | 47 | 0,979 (46/47) | 0,000 |
| Một Khoản của văn bản khác lĩnh vực | 50 | 1,000 (50/50) | 0,000 |

Theo Bảng 5.7, verify (b) bắt được 96/97 trích dẫn sai mà không gỡ nhầm mã đúng nào trong cùng câu trả lời. Ở các cấu hình không có verify (b) (`no_verify`, `baseline`), tỷ lệ phát hiện bằng 0 theo cách dựng phép thử. Đặt cạnh kết quả mục 5.4.1, verify (b) là một lớp phòng vệ: trên dữ liệu sạch nó tốn khoảng 3,4 điểm recall, đổi lại hệ thống gần như không để lọt trích dẫn sai khi mô hình sinh nhầm.

### 5.4.4. Hai phiên bản verify

Phiên bản đầu của verify (b) chỉ cho mô hình xem nội dung Khoản, không có tên Điều. Trên 179 câu, nó gỡ 63 mã trích dẫn, trong đó 47 mã là căn cứ chuẩn. Phiên bản hiện tại thêm tên văn bản, số và tên Điều vào prompt. Số mã bị gỡ còn 28 (21 là căn cứ chuẩn), số câu phải sinh lại giảm từ 21 xuống 14. Citation Recall của `full` tăng từ 0,784 lên 0,830, Citation Precision từ 0,840 lên 0,850, đúng phiên bản từ 0,667 lên 0,833.
<!-- nguồn: eval/results/v1_vs_v2.md -->

### 5.4.5. Độ trễ

<!-- nguồn: eval/results/agent_rq3_latency.md -->
Bảng 5.8 ghi độ trễ đo trên 19 câu (mẫu phân tầng cố định `subset_rq3_20.json`, đo ngày 03/11/2026). Mỗi cấu hình chạy với một bộ đệm LLM trống riêng, vì các cấu hình có chung prompt, dùng chung bộ đệm thì sẽ trúng kết quả của nhau. Khi API lỗi thì không thử lại, câu lỗi được chạy lại với bộ đệm mới. Bảng chỉ tính câu mà mọi lượt gọi LLM đều là gọi API thật (ghi trong trace). Thời gian đã trừ phần chờ giãn cách của gói API miễn phí và gồm cả truy xuất, rerank trên CPU.

**Bảng 5.8.** Độ trễ mỗi câu hỏi theo cấu hình.

| Cấu hình | n | Trung vị (s) | p90 (s) | Lượt LLM/câu |
|---|---|---|---|---|
| baseline | 19 | 6,9 | 12,0 | 1,0 |
| full | 18 | 15,9 | 26,3 | 3,8 |
| no_router | 18 | 12,7 | 25,4 | 3,2 |
| no_grading | 18 | 8,8 | 21,2 | 2,9 |
| no_verify | 18 | 11,0 | 30,0 | 2,8 |

Ba câu (một ở mỗi cấu hình `full`, `no_router`, `no_grading`) bị loại vì có lượt gọi LLM trùng đầu vào với một lượt trước đó trong cùng câu nên lấy từ bộ đệm; một câu của `no_verify` bị loại vì API báo quá tải (503) và không chạy lại được trong ngày đo.

Ở cấu hình `full`, trung vị thời gian theo bước là truy xuất 5,5 s (phần lớn là rerank trên CPU), sinh câu trả lời 2,3 s, verify 2,2 s, route 1,9 s, grade 1,4 s. Từ đó:

- `baseline` mất khoảng 7 giây dù chỉ gọi LLM một lần, chủ yếu do truy xuất và rerank.
- `full` chậm gấp khoảng 2,3 lần `baseline` (trung vị 15,9 s so với 6,9 s) vì thêm 3 lượt LLM, và câu nào cần viết lại truy vấn thì thêm một vòng truy xuất. p90 khoảng 26 giây.
- `no_grading` có trung vị 8,8 s, thấp hơn `full` 7,1 s. Con số này không có nghĩa bước grade tốn 7 giây: riêng grade chỉ mất trung vị 1,4 s và chỉ 1 câu trong mẫu có vòng truy xuất lại. Phần chênh còn lại là do các bước route, generate, verify chạy nhanh hơn ở lần đo `no_grading`, tức thời gian phản hồi của API dao động giữa hai lần đo. <!-- nguồn: trace trong eval/results/agent_rq3_latency.jsonl -->
- Mỗi lượt LLM của gói miễn phí mất khoảng 1,5–2,5 giây. Thời gian người dùng thực sự phải chờ còn cộng thêm phần giãn cách 15 lượt/phút của gói miễn phí (đã trừ khỏi bảng).

## 5.5. RQ4: Chính sách lọc theo hiệu lực

Bảng 5.9 ghi kết quả của ba chính sách lọc, Bảng 5.10 ghi chênh lệch ghép cặp so với `event`, Hình 5.4 biểu diễn ba chỉ số chính.

**Bảng 5.9.** Ba chính sách trên 32 câu có mốc thời gian (cấu hình `full`).
<!-- nguồn: eval/results/agent_rq4.md -->

| Chính sách | Trả lời | Cit. P | Cit. R | Đúng phiên bản | Correctness |
|---|---|---|---|---|---|
| event (theo ngày sự việc) | 0,781 | 0,907 | 0,781 | 0,750 | 0,766 |
| current (chỉ văn bản còn hiệu lực) | 0,719 | 0,606 | 0,469 | 0,438 | 0,578 |
| any (không lọc) | 0,875 | 0,764 | 0,625 | 0,562 | 0,703 |

**Bảng 5.10.** Chênh lệch so với `event`.
<!-- nguồn: eval/results/agent_rq4.md (32 câu), agent_rq4_heldout20.md (20 câu giữ riêng) -->

| Chính sách | Tập | Cit. R | Đúng phiên bản | Correctness |
|---|---|---|---|---|
| current | 32 câu | −0,312* [−0,500; −0,156] | −0,312* [−0,500; −0,156] | −0,188* [−0,344; −0,062] |
| any | 32 câu | −0,156 [−0,344; 0,031] | −0,188 [−0,375; 0,000] | −0,062 [−0,219; 0,094] |
| current | 20 câu giữ riêng | −0,250* [−0,450; −0,050] | −0,250* [−0,450; −0,050] | −0,150 [−0,300; 0,000] |
| any | 20 câu giữ riêng | −0,200 [−0,400; 0,000] | −0,250 [−0,500; 0,000] | −0,100 [−0,300; 0,100] |

<!-- Hình 5.4: docs/report/figures/rq4.png -->
**Hình 5.4.** Recall, đúng phiên bản và Correctness theo chính sách lọc.

Giả thuyết chốt trước H2 là `event` hơn cả `current` và `any` về đúng phiên bản.

- Giả thuyết `event` hơn `current` được ủng hộ. Chênh lệch có ý nghĩa trên cả 32 câu lẫn 20 câu giữ riêng. Chỉ lấy văn bản còn hiệu lực thì BLLĐ 2012 bị loại hẳn, mọi sự việc trước 2021 bị trả lời theo luật mới hoặc bị từ chối.
- Giả thuyết `event` hơn `any` chưa được ủng hộ đủ mạnh. `any` kém `event` 0,188 (32 câu) và 0,250 (20 câu) về đúng phiên bản, nhưng khoảng tin cậy chạm 0. Không lọc thì cả hai phiên bản có thể cùng xuất hiện trong ngữ cảnh, và mô hình nhiều lúc tự chọn đúng phiên bản theo ngày nêu trong câu hỏi; có 2/32 câu trích cả hai phiên bản. `any` trả lời nhiều nhất (0,875). Citation Precision trung bình của `any` thấp hơn (0,764 so với 0,907), nhưng hai số này tính trên hai tập câu có trích dẫn khác nhau. So ghép cặp trên 20 câu mà cả hai chính sách cùng có trích dẫn thì chênh lệch chỉ −0,042 [−0,183; 0,075], không có ý nghĩa. <!-- nguồn: eval/results/agent_rq4.md, bảng chênh lệch -->

## 5.6. Phân tích lỗi

Cấu hình `full` có 72/209 câu có ít nhất một dấu hiệu chưa tốt theo chỉ số (từ chối nhầm, thiếu căn cứ chuẩn, trích thừa, sai phiên bản hoặc Correctness < 1). Nhóm lấy mẫu 20 câu, phân tầng theo dấu hiệu, rồi một thành viên đọc từng câu (câu hỏi, đáp án mẫu, căn cứ chuẩn, căn cứ đã trích, toàn văn Điều liên quan) để gán loại lỗi. Danh mục định trước có 7 loại lỗi. Sau lượt gán đầu, 10/20 câu rơi vào "khác", nên nhóm tách thêm 4 loại từ chính ghi chú của người gán (Bảng 5.11).

**Bảng 5.11.** Loại lỗi trên 20 câu của cấu hình `full` (một câu có thể thuộc nhiều loại).
<!-- nguồn: eval/results/errors_rq3.md, errors_rq3.csv (python -m eval.error_analysis report) -->

| Nhóm | Loại lỗi | Số câu | Ví dụ |
|---|---|---|---|
| Lỗi của hệ thống | Trích dẫn không hỗ trợ nội dung câu | 5 | Z_40cab1ef, Z_1a6404b7, M_041 |
| | Từ chối nhầm | 3 | Z_0d0c6088, M_051, Z_57aadc7a |
| | Định tuyến sai (xếp nhầm là ngoài phạm vi) | 2 | M_051, Z_57aadc7a |
| | Truy xuất sai Điều | 2 | DN_010, M_051 |
| | Trả lời thiếu điều kiện, con số câu hỏi cần | 2 | M_043, LD_013 |
| | Lấy nhầm văn bản | 1 | Z_7c95f6ee |
| Chỉ số báo nhầm | Trích thêm Điều có liên quan ngoài căn cứ chuẩn | 4 | M_023, Z_4824d7b0, DS_006 |
| | Bộ chấm trừ điểm vì thiếu chi tiết câu hỏi không hỏi | 2 | M_004, DN_008 |
| | Đáp án mẫu gây tranh cãi | 1 | TM_012 |
| | Không phải lỗi (từ chối thận trọng, hợp lý) | 1 | Z_212e7377 |

Tính theo câu, 12/20 câu là lỗi thật của hệ thống và 8/20 câu là chỉ số báo nhầm. Có bốn nhận xét.

1. Trích dẫn "gần đúng" lọt qua verify (b). Cả 5 câu có trích dẫn không hỗ trợ đều đã qua verify (b) mà không bị gỡ. Đoạn bị trích thường cùng chủ đề nhưng không phải căn cứ trực tiếp. Ví dụ M_041 trích Điều 214 khoản 5 BLLĐ 2019 (thanh tra lao động "xử lý theo thẩm quyền" vi phạm) để khẳng định giới hạn thẩm quyền tuyên bố hợp đồng vô hiệu; DS_002 trích Điều 138 khoản 3 BLDS 2015 (người đại diện theo ủy quyền) cho câu về giao dịch của người từ 15 đến dưới 18 tuổi. Đặt cạnh phép thử ở mục 5.4.3 (bắt 96/97 mồi) thì thấy verify (b) bắt tốt trích dẫn lạc đề nhưng yếu với trích dẫn liên quan một phần do chính mô hình sinh ra. Dùng cùng một mô hình nhỏ để vừa sinh vừa kiểm thì bị giới hạn này.
2. Router quá chặt với câu dân sự đời thường. 2/3 câu từ chối nhầm là do router xếp câu hỏi là ngoài phạm vi: M_051 (tạm ứng lương, BLLĐ 2019 Điều 101) và Z_57aadc7a (quyền xác định dân tộc, BLDS 2015 Điều 29). Lỗi này cùng dạng với lỗi đã sửa ở prompt router trước đó, tức quy tắc phạm vi vẫn chưa bao quát hết. Ngoài mẫu 20 câu, M_066 (hỏi thẳng một Điều của BLLĐ 2012 đã hết hiệu lực, không nêu ngày sự việc) bị từ chối vì bước tra cứu trực tiếp lọc theo văn bản còn hiệu lực. Nhóm đã sửa lỗi này sau đánh giá (bước tra cứu trực tiếp không lọc hiệu lực khi câu hỏi không nêu ngày sự việc). Số liệu trong chương này là của phiên bản trước khi sửa và không chạy lại, vì trong tập kiểm thử chỉ M_066 bị ảnh hưởng.
3. Chỉ số trích dẫn phạt cả căn cứ bổ sung hợp lý. 4 câu bị tính Citation Precision thấp chỉ vì trích thêm Điều có liên quan (ví dụ Z_4824d7b0 kết hợp quy tắc chung của BLDS với quy tắc chuyên ngành của Luật Thương mại về chuyển rủi ro) mà căn cứ chuẩn chỉ có một Điều. M_023 còn bị tính sai phiên bản chỉ vì trích thêm Luật Doanh nghiệp 2020, do chỉ số đúng phiên bản hiện xét mọi văn bản được trích chứ không riêng văn bản lao động. Citation Precision trong mục 5.4 vì thế là cận dưới.
4. Bộ chấm không ổn định theo hướng. Kiểm định ở mục 5.1.4 cho thấy bộ chấm dễ dãi (cho 1 ở mọi câu trong mẫu), vậy mà ở đây có 2 câu bộ chấm cho Correctness 0,5 dù câu trả lời đúng điều câu hỏi hỏi, chỉ thiếu chi tiết phụ trong đáp án mẫu (trường hợp R5 trong thang chấm). Vì vậy chỉ nên đọc Correctness như chỉ số bổ trợ.

## 5.7. Thảo luận và giới hạn

Truy xuất lai kèm rerank đạt chỉ tiêu (Hit@5 0,844, Recall@10 0,872 trên câu Zalo), và phân đoạn theo cấu trúc luật hơn hẳn cắt cố định. Trong tác tử, router có tác dụng rõ nhất vì trích được ngày sự việc để chọn đúng phiên bản luật. Verify (b) đổi một phần recall lấy khả năng chặn trích dẫn sai, còn bước grade chưa cho thấy lợi ích trên tập này.

Về khả năng ứng dụng thực tế, hệ thống đã chạy được như một ứng dụng web gồm API FastAPI, giao diện hiển thị trích dẫn bấm được cùng các bước của tác tử (mục 4.5), kèm cấu hình Docker Compose để triển khai. Về độ chính xác, cấu hình `full` trả lời 0,871 số câu. Trung bình khoảng 13% mã trích dẫn trong một câu trả lời không thuộc căn cứ chuẩn (Citation Precision 0,870, là cận dưới theo mục 5.6), và 1/4 số câu có mốc thời gian vẫn trích sai phiên bản (0,750). Mức này hợp với một công cụ tra cứu tham khảo, nơi người dùng bấm vào trích dẫn để đọc nguyên văn Điều, Khoản và tự kiểm chứng, nhưng chưa đủ để dùng câu trả lời như ý kiến tư vấn mà không kiểm tra lại. Về vận hành, mỗi câu cần khoảng 4 lượt LLM, trung vị 15,9 giây (mục 5.4.5). Với hạn mức 500 lượt/ngày của gói miễn phí, một khóa API phục vụ được khoảng 125 câu hỏi mỗi ngày. Muốn đưa vào sử dụng rộng hơn thì cần mở rộng kho sang văn bản dưới luật và văn bản hợp nhất, dùng gói API trả phí hoặc mô hình lớn hơn, và chạy reranker trên GPU.

Đề tài có bảy giới hạn chính:

1. Prompt được chỉnh sau khi thấy lỗi trên tập kiểm thử. Đề tài không có tập phát triển riêng, hai lỗi (router từ chối nhầm câu dân sự, verify gỡ nhầm trích dẫn đúng) được phát hiện và sửa ngay trên tập kiểm thử. Nhóm chỉ viết quy tắc tổng quát, không chép câu kiểm thử vào prompt, và dùng tập giữ riêng 30 câu soạn sau khi chốt prompt để kiểm tra lại. Kết quả trên tập giữ riêng cùng chiều với tập cũ.
2. Kiểm định bộ chấm còn yếu. Chỉ có một người chấm tay, cũng là người xây dựng hệ thống. Bộ chấm cho điểm tối đa ở mọi câu trong mẫu nên chưa chứng minh được khả năng phân biệt câu sai.
3. Router còn xếp nhầm. Trên 209 câu, router xếp nhầm 3 câu trong phạm vi thành ngoài phạm vi (khoảng 1,5%; M_051, Z_50541f81, Z_57aadc7a), trong khi bắt đúng 5/5 câu ngoài phạm vi. Nhóm không sửa prompt router lần nữa vì tập giữ riêng đã dùng, không còn dữ liệu sạch để kiểm bản sửa.
4. Cỡ mẫu nhỏ. Nhiều chênh lệch cùng chiều nhưng chưa có ý nghĩa (router với Correctness; `event` so với `any`). Ước tính cần vài trăm câu có mốc thời gian để các chênh lệch cỡ này có ý nghĩa.
5. Phạm vi văn bản hẹp. Kho chỉ có 5 văn bản, bản gốc chưa hợp nhất sửa đổi, không có Nghị định, Thông tư hướng dẫn. Câu hỏi cần văn bản dưới luật sẽ bị từ chối hoặc trả lời thiếu.
6. Hạn mức API miễn phí. Mô hình tác tử bị giới hạn 500 lượt/ngày và hay báo quá tải, mọi cấu hình phải dùng cùng một mô hình nhỏ (`gemini-3.1-flash-lite`). Với mô hình lớn hơn, kết quả có thể khác.
7. Reranker cắt đoạn dài. Cross-encoder chỉ đọc tối đa 512 token cho cặp (câu hỏi, đoạn). 56/1.693 Điều (3,3%) dài hơn mức này nên rerank không xét tới phần cuối Điều, còn ở cấp Khoản chỉ 3/4.853 đoạn (0,1%) bị ảnh hưởng. Do đó biến thể cấp Điều ở RQ2 có thể bị đánh giá thấp hơn đôi chút, dù vẫn cao nhất trên câu Zalo.
