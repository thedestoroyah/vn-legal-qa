# CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI

> **Bản nháp H15** — Hùng, 29/10/2026; **cập nhật H17** — Đạt, 10/11/2026 (tập kiểm thử 209 câu, tập giữ riêng, giao diện, kiểm định bộ chấm, lịch). Viết bằng Markdown để chép vào file báo cáo theo mẫu khoa.
> Quy ước trích dẫn: chỉ dùng tài liệu ở mục 12 đề cương. Tài liệu ngoài danh sách gắn `[CẦN KIỂM TRA]` để Đạt tra lại trước khi đưa vào bản chính. Kiểm 10/11: không còn chỗ nào gắn nhãn này.
> Số liệu lấy từ repo ngày 10/11 (`eval/test_cases.json`). Kiểm tra lại trước khi nộp nếu tập kiểm thử thay đổi.
> Sửa văn phong 18/11: bỏ in đậm trong thân bài, gạch ngang, mũi tên; số liệu giữ nguyên.

## 1.1. Đặt vấn đề

### 1.1.1. Nhu cầu tra cứu pháp luật

Hệ thống pháp luật Việt Nam gồm rất nhiều văn bản quy phạm pháp luật. Mỗi văn bản có cấu trúc phân cấp gồm Phần, Chương, Mục, Điều, Khoản và Điểm, và các văn bản còn sửa đổi, bổ sung, thay thế hoặc dẫn chiếu lẫn nhau. Người không có chuyên môn pháp lý, như sinh viên, người lao động hay chủ doanh nghiệp nhỏ, khó xác định đúng điều luật áp dụng cho tình huống của mình. Họ thường hỏi bằng lời thường ("công ty trả lương chậm thì tôi có được nghỉ việc ngay không?"), còn văn bản lại dùng thuật ngữ pháp lý ("đơn phương chấm dứt hợp đồng lao động", "không được trả lương đầy đủ hoặc trả lương không đúng thời hạn"). Vì thế tìm kiếm theo từ khóa thông thường dễ bỏ sót hoặc trả về điều luật không liên quan.

### 1.1.2. Cơ hội và hạn chế của mô hình ngôn ngữ lớn

Mô hình ngôn ngữ lớn (LLM) trả lời được câu hỏi bằng ngôn ngữ tự nhiên, nhưng có thể "bịa" nội dung (hallucination) và trích dẫn sai. Với pháp luật, rủi ro này rất nặng: một câu trả lời nghe hợp lý nhưng dựa trên điều luật không tồn tại hoặc đã hết hiệu lực có thể khiến người dùng quyết định sai. Kỹ thuật Retrieval-Augmented Generation (RAG) giảm rủi ro bằng cách truy xuất các đoạn văn bản liên quan rồi yêu cầu LLM trả lời dựa trên các đoạn đó (Lewis và cộng sự, 2020). Tuy vậy, Gao và cộng sự (2023) cho thấy ngay cả mô hình mạnh vẫn thường sinh trích dẫn không hỗ trợ cho khẳng định đi kèm. Do đó hệ thống hỏi đáp pháp luật cần thêm bước kiểm chứng trích dẫn sau khi sinh câu trả lời.

### 1.1.3. Vấn đề hiệu lực theo thời gian

Pháp luật có hiệu lực theo thời gian: cùng một vấn đề, sự việc xảy ra vào thời điểm khác nhau thì có thể thuộc phạm vi điều chỉnh của văn bản khác nhau. Ví dụ, Bộ luật Lao động 2012 có hiệu lực từ 01/05/2013 đến hết 31/12/2020, sau đó Bộ luật Lao động 2019 thay thế và có hiệu lực từ 01/01/2021. Một số quy định thay đổi rõ giữa hai bộ luật:

- Bộ luật Lao động 2012 có ba loại hợp đồng lao động, trong đó có hợp đồng theo mùa vụ hoặc theo một công việc nhất định dưới 12 tháng (Điều 22). Bộ luật Lao động 2019 chỉ còn hai loại: không xác định thời hạn và xác định thời hạn (Điều 20).
- Theo Bộ luật Lao động 2012, người lao động làm hợp đồng xác định thời hạn chỉ được đơn phương chấm dứt hợp đồng khi có một trong các lý do luật định (Điều 37). Theo Bộ luật Lao động 2019, người lao động chỉ cần báo trước (Điều 35).

Như vậy, câu hỏi "Năm 2019, tôi muốn nghỉ việc chỉ báo trước 30 ngày có được không?" phải trả lời theo Bộ luật Lao động 2012, dù văn bản này nay đã hết hiệu lực. Nhóm khảo sát ở Chương 2 thấy hai hệ thống hỏi đáp pháp luật tiếng Việt gần với đề tài nhất đều không chọn phiên bản văn bản theo thời điểm sự việc. Hai bộ dữ liệu có công bố định dạng (Zalo AI 2021, ALQAC 2025) cũng không ghi thời điểm này, nên chưa đánh giá được loại câu hỏi trên.

### 1.1.4. Hướng tiếp cận Agentic-RAG

RAG truy xuất một lượt có mấy hạn chế: không nhận ra câu hỏi ngoài phạm vi, không biết lúc nào bằng chứng còn thiếu và không tự kiểm tra lại trích dẫn. Corrective RAG (Yan và cộng sự, 2024) và Self-RAG (Asai và cộng sự, 2024) thêm bước tự đánh giá bằng chứng và tự phê bình đầu ra. Đề tài kế thừa ý tưởng này theo hướng Agentic-RAG: tác tử tự định tuyến câu hỏi, tự đánh giá bằng chứng đã đủ chưa, viết lại truy vấn khi cần và tự kiểm chứng trích dẫn trước khi trả lời. Pham và cộng sự (2025) đã cho thấy Agentic-RAG hiệu quả với pháp luật Việt Nam, nhưng chưa xét hiệu lực theo thời gian và chưa tách riêng đóng góp của từng thành phần tác tử.

## 1.2. Mục tiêu đề tài

### 1.2.1. Mục tiêu tổng quát

Đề tài xây dựng một hệ thống hỏi đáp pháp luật tiếng Việt hoàn chỉnh. Hệ thống nhận câu hỏi bằng ngôn ngữ tự nhiên, truy xuất căn cứ pháp lý từ kho văn bản có cấu trúc phân cấp và sinh câu trả lời trích dẫn tới cấp Điều, Khoản, theo đúng phiên bản văn bản có hiệu lực tại thời điểm của tình huống. Người dùng hỏi đáp qua giao diện web.

### 1.2.2. Mục tiêu cụ thể

1. Xây dựng kho dữ liệu có cấu trúc: chuẩn hóa 5 văn bản thuộc 4 lĩnh vực (Dân sự, Lao động, Doanh nghiệp, Thương mại), phân đoạn theo cấp Chương, Mục, Điều, Khoản và gắn siêu dữ liệu khoảng hiệu lực.
2. Cài đặt và so sánh nhiều phương pháp truy xuất: BM25, tìm kiếm ngữ nghĩa (dense), tìm kiếm lai bằng Reciprocal Rank Fusion và xếp hạng lại bằng cross-encoder. Chỉ tiêu là Hit Rate@5 ≥ 80% và Recall@10 ≥ 75%.
3. Xây dựng tác tử Agentic-RAG có kiểm chứng trích dẫn. Đồ thị trạng thái gồm các bước định tuyến, truy xuất có lọc hiệu lực, đánh giá bằng chứng và viết lại truy vấn, sinh câu trả lời, kiểm chứng trích dẫn hai lớp. Chỉ tiêu Citation Precision ≥ 85%. Hệ thống từ chối khi câu hỏi ngoài phạm vi hoặc không đủ căn cứ.
4. Làm ứng dụng web: giao diện NiceGUI gọi backend FastAPI. Người dùng bấm vào trích dẫn để đọc toàn văn điều luật và xem tác tử đã đi qua những bước nào.
5. Lập bộ dữ liệu kiểm thử và đánh giá gồm 209 câu hỏi từ ba nguồn, trong đó có tập giữ riêng 30 câu soạn sau khi đã cố định prompt. Bộ này dùng để đo chất lượng truy xuất, trích dẫn, câu trả lời, độ đúng phiên bản và chi phí.

### 1.2.3. Câu hỏi nghiên cứu

Đề tài trả lời bốn câu hỏi nghiên cứu.

RQ1 (chiến lược truy xuất). Kết hợp tìm kiếm từ khóa BM25 với tìm kiếm ngữ nghĩa bằng Reciprocal Rank Fusion, rồi xếp hạng lại bằng cross-encoder, thì truy xuất căn cứ pháp lý tiếng Việt tốt hơn từng phương pháp đơn lẻ bao nhiêu? Nhóm so sánh bốn cấu hình BM25, Dense, Hybrid và Hybrid kèm xếp hạng lại theo Hit Rate@5, Recall@10 và MRR@10.

RQ2 (phân đoạn và cấu trúc phân cấp). So với phân đoạn cố định theo số từ, phân đoạn theo cấu trúc pháp lý ảnh hưởng thế nào đến hiệu quả truy xuất và hiện tượng truy xuất nhầm văn bản (Document-Level Retrieval Mismatch, DRM; Reuter và cộng sự, 2025)? Nhóm so sánh bốn cách: phân đoạn cố định, theo Điều, theo Khoản và theo Khoản có gắn tiêu đề phân cấp. Cả bốn đều đánh giá ở cấp Điều.

RQ3 (Agentic-RAG). Tác tử biết tự định tuyến, tự đánh giá bằng chứng và tự kiểm chứng trích dẫn cải thiện chất lượng câu trả lời và độ chính xác trích dẫn bao nhiêu so với RAG truy xuất một lượt, và tốn thêm bao nhiêu chi phí? Nhóm làm nghiên cứu lược bỏ (ablation): lần lượt tắt từng thành phần của tác tử rồi đo Citation Precision/Recall, Faithfulness, Answer Correctness, độ trễ và số lượt gọi LLM.

RQ4 (hiệu lực theo thời gian). Khi kho dữ liệu chứa cả văn bản còn hiệu lực lẫn văn bản đã hết hiệu lực về cùng một vấn đề, hệ thống có trích đúng phiên bản có hiệu lực tại thời điểm xảy ra sự việc không? Nhóm so sánh ba chính sách: không lọc, chỉ giữ văn bản "còn hiệu lực" và lọc theo thời điểm sự việc do tác tử trích ra từ câu hỏi.

## 1.3. Đối tượng và phạm vi nghiên cứu

### 1.3.1. Đối tượng nghiên cứu

Đề tài nghiên cứu ba đối tượng: (1) truy xuất căn cứ pháp lý có xét cấu trúc phân cấp và hiệu lực theo thời gian của văn bản; (2) tác tử Agentic-RAG điều phối truy xuất và sinh câu trả lời; (3) cơ chế sinh và kiểm chứng trích dẫn.

### 1.3.2. Phạm vi dữ liệu

Kho dữ liệu gồm 5 văn bản luật:

| Mã | Văn bản | Số hiệu | Số Điều | Trạng thái |
|---|---|---|---|---|
| BLDS2015 | Bộ luật Dân sự 2015 | 91/2015/QH13 | 689 | Còn hiệu lực |
| BLLD2019 | Bộ luật Lao động 2019 | 45/2019/QH14 | 220 | Còn hiệu lực |
| LDN2020 | Luật Doanh nghiệp 2020 | 59/2020/QH14 | 218 | Còn hiệu lực |
| LTM2005 | Luật Thương mại 2005 | 36/2005/QH11 | 324 | Còn hiệu lực |
| BLLD2012 | Bộ luật Lao động 2012 | 10/2012/QH13 | 242 | Hết hiệu lực từ 01/01/2021 (chỉ dùng cho RQ4) |

Đơn vị truy xuất là Khoản, các Điểm nằm trong Khoản. Khi cần, hệ thống lấy được toàn văn Điều chứa Khoản đó.

Tập kiểm thử gồm 209 câu hỏi từ ba nguồn, kết quả báo cáo tách riêng theo nguồn:

- 77 câu do người viết, chọn lọc từ bộ Zalo AI Legal Text Retrieval 2021 (Zalo AI, 2021), gán nhãn cấp Điều.
- 65 câu tổng hợp (synthetic) sinh bằng LLM, trong đó 20 câu được kiểm định tay.
- 67 câu nhóm tự soạn: 15 câu tình huống, 32 câu có mốc thời gian, 15 câu tra cứu trực tiếp và 5 câu ngoài phạm vi.

Trong 67 câu tự soạn có 30 câu (M_038 tới M_067, gồm 20 câu có mốc thời gian và 10 câu tra cứu trực tiếp) làm tập giữ riêng. Nhóm soạn và chốt 30 câu này sau khi prompt của tác tử đã cố định, trước khi chạy hệ thống trên câu nào trong số đó. Prompt từng được chỉnh khi thấy lỗi trên các câu cũ, nên tập giữ riêng cho biết kết quả có giữ được trên những câu không dùng để chỉnh hay không (mục 5.1.1).

### 1.3.3. Giới hạn

- Không gồm Nghị định, Thông tư hướng dẫn, án lệ và bản án.
- Dùng văn bản gốc khi ban hành, chưa hợp nhất các lần sửa đổi, bổ sung (ví dụ các luật sửa đổi Luật Doanh nghiệp 2020).
- Hiệu lực xét ở cấp văn bản, chưa xét trường hợp từng Điều, Khoản bị sửa đổi.
- LLM dùng qua API miễn phí (Gemini, Groq). Embedding và reranker chạy cục bộ trên CPU. Không fine-tune mô hình.
- Hệ thống chỉ là công cụ tham khảo, không thay thế tư vấn của luật sư.

## 1.4. Phương pháp thực hiện

Đề tài thực hiện từ 15/08 đến 04/12/2026 theo mô hình Agile/Scrum rút gọn. Sau giai đoạn khảo sát và viết đề cương (15/08 đến 08/10), phần triển khai gồm 6 sprint từ 09/10 đến 27/11, tuần cuối dành cho rà soát và nộp. Phạm Huỳnh Quốc Đạt phụ trách lõi kỹ thuật (truy xuất, tác tử, API, đánh giá tự động). Hoàng Sinh Hùng phụ trách dữ liệu (kho văn bản, tập kiểm thử), giao diện và báo cáo. Việc đánh giá gồm hai phần:

- Các chỉ số truy xuất, trích dẫn và phiên bản tính tự động bằng cách đối chiếu với nhãn chuẩn.
- Chất lượng câu trả lời chấm bằng LLM-as-a-judge: Faithfulness theo định nghĩa của RAGAS (Es và cộng sự, 2024), Answer Correctness (so với đáp án mẫu) theo thư viện ragas. Bộ chấm được kiểm định bằng cách so với điểm chấm tay độc lập của một thành viên trên 20 câu trả lời (mục 5.1.4).

Mã nguồn, dữ liệu đã xử lý, tập kiểm thử và bản nháp báo cáo nằm chung trong một kho Git trên GitHub. Mỗi sprint có một kế hoạch cho phần lõi kỹ thuật và các thẻ việc tự chứa cho thành viên còn lại, lưu ngay trong kho, và tiến độ báo cáo hằng tuần với giảng viên hướng dẫn. Mỗi commit ứng với một việc và ghi rõ loại thay đổi (tính năng, sửa lỗi, dữ liệu, tài liệu). Bộ kiểm thử tự động (pytest, hơn 380 ca kiểm thử) phải chạy qua trước khi commit. Hệ thống đóng gói bằng Docker Compose, tệp README liệt kê lệnh tái tạo từng bảng số liệu ở Chương 5.

## 1.5. Đóng góp chính

1. Kho văn bản pháp luật có cấu trúc kèm khoảng hiệu lực. 5 văn bản được bóc tách thành cây Chương/Mục/Điều/Khoản/Điểm, mỗi đoạn mang ngày có hiệu lực và ngày hết hiệu lực. Kho có một văn bản đã hết hiệu lực để nghiên cứu hiệu lực theo thời gian.
2. Truy xuất theo khoảng hiệu lực tại thời điểm của tình huống. Tác tử trích thời điểm sự việc từ câu hỏi rồi chỉ truy xuất văn bản có hiệu lực tại thời điểm đó. Hiệu quả đo bằng tỷ lệ trích đúng phiên bản (RQ4).
3. Tác tử Agentic-RAG có kiểm chứng trích dẫn hai lớp. Lớp thứ nhất đối chiếu mã trích dẫn với ngữ cảnh, lớp thứ hai dùng LLM kiểm từng cặp (khẳng định, đoạn luật). Tác tử từ chối khi câu hỏi ngoài phạm vi hoặc không đủ căn cứ.
4. Đánh giá tách riêng từng thành phần bằng nghiên cứu lược bỏ trên 5 cấu hình (baseline, full, no_router, no_grading, no_verify), báo cáo cả chất lượng lẫn chi phí (độ trễ, số lượt gọi LLM).
5. Bộ kiểm thử ba nguồn có nhãn căn cứ chuẩn, cùng ứng dụng web hiển thị trích dẫn bấm được và các bước của tác tử.

## 1.6. Ý nghĩa khoa học và thực tiễn

Về khoa học, đề tài đưa hiệu lực theo thời gian vào cả thiết kế lẫn đánh giá hệ thống hỏi đáp pháp luật tiếng Việt. Các câu hỏi có mốc thời gian được gắn nhãn phiên bản văn bản đúng, nhờ vậy đo được hệ thống có chọn đúng phiên bản theo thời điểm sự việc không, loại câu hỏi mà hai bộ dữ liệu công khai đã khảo sát chưa đo được. Đề tài cũng đánh giá riêng từng thành phần của tác tử bằng nghiên cứu lược bỏ, so sánh ghép cặp theo câu kèm khoảng tin cậy, và đo trực tiếp khả năng chặn trích dẫn sai bằng phép thử tiêm trích dẫn, thay vì chỉ báo cáo kết quả của hệ thống hoàn chỉnh.

Về thực tiễn, người tra cứu nhận câu trả lời kèm trích dẫn tới Khoản và bấm vào để đọc nguyên văn. Câu trả lời dựa trên văn bản có hiệu lực vào thời điểm sự việc, không mặc định lấy luật hiện hành. Khi câu hỏi ngoài phạm vi hoặc không đủ căn cứ, hệ thống từ chối thay vì đoán. Hệ thống chạy trên CPU với API mô hình ngôn ngữ miễn phí nên chi phí triển khai thấp. Mục 5.7 phân tích mức độ sẵn sàng ứng dụng.

## 1.7. Bố cục báo cáo

Báo cáo gồm sáu chương:

- Chương 1 (Tổng quan đề tài) đặt vấn đề, nêu mục tiêu, câu hỏi nghiên cứu, phạm vi và đóng góp.
- Chương 2 (Tổng quan tài liệu) điểm lại các nghiên cứu liên quan trên thế giới và trong nước, vấn đề còn tồn tại và hướng tiếp cận của đề tài.
- Chương 3 (Cơ sở lý thuyết) trình bày BM25, truy xuất dày đặc, RRF, cross-encoder, RAG, Agentic-RAG, LangGraph và đặc thù văn bản pháp luật Việt Nam.
- Chương 4 (Phân tích và thiết kế hệ thống) mô tả kiến trúc tổng thể, pipeline dữ liệu, động cơ truy xuất, tác tử, API và giao diện.
- Chương 5 (Thực nghiệm và đánh giá) trình bày tập kiểm thử, các chỉ số, kết quả RQ1 tới RQ4 và phân tích lỗi.
- Chương 6 (Kết luận và hướng phát triển) tổng kết kết quả, hạn chế và hướng mở rộng.
