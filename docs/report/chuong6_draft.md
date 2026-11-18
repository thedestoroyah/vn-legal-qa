# CHƯƠNG 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

> **Bản nháp H21** — Đạt, 10/11/2026. Mọi con số lấy từ `docs/report/chuong5_draft.md` (nguồn gốc ghi trong comment của từng bảng ở Chương 5); không có số nào mới.
> Ký hiệu: chênh lệch "có ý nghĩa" nghĩa là khoảng tin cậy bootstrap 95% của hiệu số ghép cặp không chứa 0 (mục 5.1.3).

## 6.1. Kết luận

### 6.1.1. Kết quả đạt được

Đề tài đã xây dựng một hệ thống hỏi đáp pháp luật tiếng Việt theo hướng Agentic-RAG trên kho 5 văn bản luật, trong đó có Bộ luật Lao động 2012 đã hết hiệu lực. Hệ thống gồm pipeline bóc tách văn bản thành Chương/Mục/Điều/Khoản/Điểm kèm khoảng hiệu lực, bộ truy xuất lai có lọc theo hiệu lực, tác tử LangGraph (định tuyến, truy xuất, đánh giá bằng chứng, sinh câu trả lời, kiểm chứng trích dẫn hai lớp), API FastAPI và giao diện web. Nhóm đánh giá hệ thống trên 209 câu hỏi từ ba nguồn, trong đó có tập giữ riêng 30 câu soạn sau khi đã cố định prompt.

Hệ thống đạt cả ba chỉ tiêu định lượng đặt ra ở mục 1.2.2 (Bảng 6.1).

**Bảng 6.1.** Chỉ tiêu và kết quả.

| Chỉ tiêu | Mục tiêu | Kết quả | Nguồn |
|---|---|---|---|
| Hit@5 (Hybrid + rerank, 77 câu Zalo) | ≥ 0,80 | 0,844 | Bảng 5.2 |
| Recall@10 (Hybrid + rerank, 77 câu Zalo) | ≥ 0,75 | 0,872 | Bảng 5.2 |
| Citation Precision (cấu hình `full`, 209 câu) | ≥ 0,85 | 0,870 | Bảng 5.4 |

### 6.1.2. Trả lời các câu hỏi nghiên cứu

Với RQ1 (chiến lược truy xuất), trên câu hỏi đời thường của bộ Zalo, tìm kiếm ngữ nghĩa hơn hẳn BM25 (Hit@5 0,844 so với 0,766). Hợp nhất bằng RRF không làm tăng Hit@5 so với Dense (0,805 so với 0,844). Phần lợi nằm ở bước xếp hạng lại: MRR@10 tăng từ 0,748 lên 0,807, tức Điều đúng lên vị trí cao hơn, đổi lại rerank trên CPU mất khoảng 6,8 giây mỗi câu. Hybrid + rerank là cấu hình tốt nhất về thứ hạng, còn Hit@5 và Recall@10 chỉ ngang Dense (cùng 0,844 và 0,872).

Với RQ2 (cách phân đoạn), phân đoạn theo cấu trúc luật hơn hẳn cắt cố định 200 từ (Hit@5 cao hơn 0,25–0,29). Trên câu Zalo, cấp Điều cao nhất (Hit@5 0,883), hợp lý vì căn cứ chuẩn của Zalo ở cấp Điều. Trên 157 câu có căn cứ chuẩn, cấp Khoản kèm tiêu đề bằng cấp Điều (Hit@5 0,924). Gắn tiêu đề phân cấp không làm Hit@5 khác đi trên câu Zalo nhưng nâng Hit@5 trên câu tổng hợp từ 0,908 lên 1,000. Khoản kèm tiêu đề cũng có tỷ lệ lấy nhầm văn bản (DRM@5) thấp nhất trên câu Zalo (0,075, so với 0,101 khi không gắn tiêu đề), nhưng chênh lệch nhỏ, chưa kiểm định và chưa đủ để quy riêng cho tiêu đề. Hệ thống giữ cấp Khoản kèm tiêu đề làm mặc định vì trích dẫn tới Khoản cụ thể hơn cho người đọc.

Với RQ3 (đóng góp của các thành phần tác tử), so với RAG một lượt (`baseline`), tác tử đầy đủ có Citation Precision cao hơn 0,060 và tỷ lệ đúng phiên bản cao hơn 0,250, cả hai đều có ý nghĩa. Chi phí là khoảng 4 lượt LLM mỗi câu thay vì 1, trung vị độ trễ 15,9 giây thay vì 6,9 giây. Xét riêng từng thành phần:

- Router có tác dụng rõ nhất. Bỏ router thì tỷ lệ đúng phiên bản giảm 0,250 (có ý nghĩa), vì không còn ngày sự việc để chọn văn bản. Giả thuyết H1 được ủng hộ ở chỉ số đúng phiên bản. Với Correctness, chênh lệch cùng chiều (−0,042 trên 209 câu, −0,083 trên tập giữ riêng) nhưng chưa có ý nghĩa, nên mới là xu hướng.
- Verify (b) là một lớp phòng vệ. Trên dữ liệu tự nhiên nó đổi một phần Citation Recall (bỏ verify thì recall tăng 0,034) lấy Citation Precision (bỏ verify thì giảm 0,016), cả hai đều có ý nghĩa. Trong phép thử tiêm trích dẫn sai, nó bắt được 96/97 trích dẫn sai mà không gỡ nhầm mã đúng nào.
- Bước grade (đánh giá bằng chứng và viết lại truy vấn) chưa cho thấy lợi ích đo được trên tập này, trong khi tốn thêm khoảng 1 lượt LLM mỗi câu.

Trên tập giữ riêng 30 câu, `full` có Citation Precision 0,978 nhưng chỉ trả lời 23/30 câu, ít hơn `no_router` (25/30), vì thiếu căn cứ đúng phiên bản thì tác tử từ chối thay vì trả lời bằng văn bản sai phiên bản. Đánh đổi giữa độ phủ và độ chính xác này hợp với yêu cầu thận trọng của lĩnh vực pháp luật, nhưng làm tăng số lần từ chối nhầm.

Với RQ4 (hiệu lực theo thời gian), lọc theo ngày sự việc (`event`) tốt hơn có ý nghĩa so với chỉ lấy văn bản còn hiệu lực (`current`): đúng phiên bản cao hơn 0,312 trên 32 câu có mốc thời gian và 0,250 trên 20 câu giữ riêng. So với không lọc (`any`), `event` cũng cao hơn về đúng phiên bản (0,188 trên 32 câu, 0,250 trên 20 câu) nhưng khoảng tin cậy chạm 0. Giả thuyết H2 vì vậy mới được ủng hộ một nửa: `event` hơn `current` đã được khẳng định, `event` hơn `any` thì chưa. Không lọc thì mô hình nhiều lúc tự chọn đúng phiên bản theo ngày nêu trong câu hỏi. Citation Precision trung bình của `any` thấp hơn (0,764 so với 0,907), nhưng so ghép cặp trên các câu cả hai cùng có trích dẫn thì chênh lệch không có ý nghĩa.

Đóng góp rõ nhất của đề tài là cơ chế truy xuất theo hiệu lực tại thời điểm sự việc. Ở cả RQ3 (router) và RQ4 (chính sách lọc), trích ngày sự việc rồi lọc văn bản theo khoảng hiệu lực cho tỷ lệ trích đúng phiên bản luật cao hơn rõ so với RAG một lượt (0,750 so với 0,500) và so với chính sách "chỉ văn bản còn hiệu lực" (0,750 so với 0,438).

## 6.2. Hạn chế

1. Prompt được chỉnh trên tập kiểm thử. Đề tài không có tập phát triển riêng, hai lỗi của prompt (router từ chối nhầm câu dân sự, verify gỡ nhầm trích dẫn đúng) được phát hiện và sửa trên chính tập kiểm thử. Tập giữ riêng 30 câu giảm được nhưng không loại bỏ hẳn giới hạn này.
2. Kiểm định bộ chấm còn yếu. Chỉ có một người chấm tay, cũng là người xây dựng hệ thống. Bộ chấm cho điểm tối đa ở mọi câu trong mẫu (kappa bằng 0), nên Faithfulness và Answer Correctness chỉ là chỉ số bổ trợ.
3. Cỡ mẫu nhỏ. Nhiều chênh lệch cùng chiều nhưng chưa có ý nghĩa (router với Correctness, `event` so với `any`), nên các kết luận này mới là xu hướng.
4. Tác tử còn lỗi. Router xếp nhầm 3/204 câu trong phạm vi thành ngoài phạm vi. Verify (b) bắt tốt trích dẫn lạc đề nhưng để lọt trích dẫn có liên quan một phần (5/20 câu trong mẫu phân tích lỗi), một phần vì cùng một mô hình nhỏ vừa sinh vừa kiểm.
5. Chỉ số trích dẫn chưa phân biệt căn cứ bổ sung hợp lý. Trích thêm Điều có liên quan ngoài căn cứ chuẩn bị tính là sai, nên Citation Precision là cận dưới. Chỉ số đúng phiên bản xét mọi văn bản được trích, không riêng văn bản lao động.
6. Phạm vi văn bản hẹp. Kho chỉ có 5 văn bản, bản gốc chưa hợp nhất sửa đổi, hiệu lực xét ở cấp văn bản, không có Nghị định, Thông tư hướng dẫn.
7. Tài nguyên có hạn. Tác tử dùng một mô hình nhỏ qua API miễn phí (giới hạn lượt gọi, hay quá tải), với mô hình lớn hơn kết quả có thể khác. Reranker chỉ đọc 512 token, nên ở phân đoạn cấp Điều, phần cuối của 3,3% số Điều không được xét (ở cấp Khoản mặc định chỉ 0,1% số đoạn).

## 6.3. Hướng phát triển

Mỗi hướng dưới đây nhắm vào một hạn chế ở mục 6.2:

1. Tách tập phát triển và tập kiểm thử (hạn chế 1). Prompt chỉnh trên tập phát triển, còn tập kiểm thử chốt trước và chỉ chạy một lần, như đã làm với tập giữ riêng.
2. Kiểm định bộ chấm chặt hơn (hạn chế 2). Cần nhiều người chấm độc lập, trong đó có người có chuyên môn luật, và đưa vào mẫu cả những câu trả lời cố ý sai để đo khả năng phân biệt của bộ chấm.
3. Mở rộng tập câu có mốc thời gian (hạn chế 3). Soạn theo cặp quy định khác nhau giữa hai phiên bản luật như tập giữ riêng, nâng lên vài trăm câu để kiểm định được các chênh lệch cỡ hiện tại.
4. Cải thiện router và verify (hạn chế 4). Khi router xếp câu hỏi là ngoài phạm vi mà truy xuất vẫn tìm được đoạn luật điểm cao thì cho tác tử thử trả lời. Bước verify nên dùng mô hình khác (hoặc mô hình suy luận ngôn ngữ tự nhiên) để không phải dùng một mô hình vừa sinh vừa kiểm.
5. Chỉ số trích dẫn nhiều mức (hạn chế 5). Gán nhãn căn cứ chuẩn theo hai mức "bắt buộc" và "chấp nhận được", và chỉ tính đúng phiên bản trên văn bản thuộc lĩnh vực có nhiều phiên bản.
6. Mở rộng kho văn bản (hạn chế 6). Hợp nhất các lần sửa đổi, bổ sung để xét hiệu lực ở cấp Điều, Khoản, thêm Nghị định, Thông tư và quan hệ dẫn chiếu giữa các văn bản.
7. Thử mô hình và reranker khác (hạn chế 7). Chạy lại thực nghiệm với mô hình lớn hơn hoặc mô hình chạy cục bộ. Điều dài thì chia thành nhiều cửa sổ để rerank rồi lấy điểm cao nhất.
