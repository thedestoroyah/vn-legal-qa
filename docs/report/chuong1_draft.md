# CHƯƠNG 1. TỔNG QUAN ĐỀ TÀI

> **Bản nháp H15** — Hùng, 29/10/2026; **cập nhật H17** — Đạt, 10/11/2026 (tập kiểm thử 209 câu, tập giữ riêng, giao diện, kiểm định bộ chấm, lịch). Viết bằng Markdown để chép vào file báo cáo theo mẫu khoa.
> Quy ước trích dẫn: chỉ dùng tài liệu ở mục 12 đề cương. Tài liệu ngoài danh sách gắn `[CẦN KIỂM TRA]` để Đạt tra lại trước khi đưa vào bản chính. Kiểm 10/11: không còn chỗ nào gắn nhãn này.
> Số liệu lấy từ repo ngày 10/11 (`eval/test_cases.json`). Kiểm tra lại trước khi nộp nếu tập kiểm thử thay đổi.

## 1.1. Đặt vấn đề

### 1.1.1. Nhu cầu tra cứu pháp luật

Pháp luật Việt Nam được thể hiện qua một khối lượng lớn văn bản quy phạm pháp luật. Mỗi văn bản có cấu trúc phân cấp gồm Phần, Chương, Mục, Điều, Khoản và Điểm. Giữa các văn bản còn có nhiều quan hệ như sửa đổi, bổ sung, thay thế và dẫn chiếu. Với người không có chuyên môn pháp lý, như sinh viên, người lao động hay chủ doanh nghiệp nhỏ, việc xác định đúng điều luật áp dụng cho một tình huống cụ thể là khó khăn. Lý do là câu hỏi thường được diễn đạt bằng ngôn ngữ đời thường ("công ty trả lương chậm thì tôi có được nghỉ việc ngay không?"), trong khi văn bản dùng thuật ngữ pháp lý ("đơn phương chấm dứt hợp đồng lao động", "không được trả lương đầy đủ hoặc trả lương không đúng thời hạn"). Tìm kiếm theo từ khóa thông thường vì vậy dễ bỏ sót hoặc trả về điều luật không liên quan.

### 1.1.2. Cơ hội và hạn chế của mô hình ngôn ngữ lớn

Các mô hình ngôn ngữ lớn (LLM) cho phép trả lời câu hỏi bằng ngôn ngữ tự nhiên, nhưng có thể "bịa" nội dung (hallucination) và đưa ra trích dẫn không chính xác. Trong lĩnh vực pháp luật, đây là rủi ro nghiêm trọng: một câu trả lời nghe hợp lý nhưng dựa trên điều luật không tồn tại hoặc đã hết hiệu lực có thể khiến người dùng đưa ra quyết định sai. Kỹ thuật Retrieval-Augmented Generation (RAG) giảm rủi ro này bằng cách truy xuất các đoạn văn bản liên quan rồi yêu cầu LLM trả lời dựa trên các đoạn đó (Lewis và cộng sự, 2020). Tuy nhiên, Gao và cộng sự (2023) chỉ ra rằng ngay cả các mô hình mạnh vẫn thường sinh trích dẫn không hỗ trợ cho khẳng định. Vì vậy, một hệ thống hỏi đáp pháp luật cần thêm cơ chế **kiểm chứng trích dẫn** sau khi sinh câu trả lời.

### 1.1.3. Vấn đề hiệu lực theo thời gian

Một đặc thù quan trọng của pháp luật là **hiệu lực theo thời gian**: cùng một vấn đề có thể được điều chỉnh bởi các văn bản khác nhau tùy thời điểm xảy ra sự việc. Ví dụ, Bộ luật Lao động 2012 có hiệu lực từ 01/05/2013 đến hết 31/12/2020, sau đó được thay thế bởi Bộ luật Lao động 2019 có hiệu lực từ 01/01/2021. Một số quy định thay đổi rõ rệt giữa hai bộ luật:

- Bộ luật Lao động 2012 có ba loại hợp đồng lao động, trong đó có hợp đồng theo mùa vụ hoặc theo một công việc nhất định dưới 12 tháng (Điều 22). Bộ luật Lao động 2019 chỉ còn hai loại: không xác định thời hạn và xác định thời hạn (Điều 20).
- Theo Bộ luật Lao động 2012, người lao động làm hợp đồng xác định thời hạn chỉ được đơn phương chấm dứt hợp đồng khi có một trong các lý do luật định (Điều 37). Theo Bộ luật Lao động 2019, người lao động chỉ cần báo trước (Điều 35).

Vì vậy, một câu hỏi như "Năm 2019, tôi muốn nghỉ việc chỉ báo trước 30 ngày có được không?" phải được trả lời theo Bộ luật Lao động 2012, dù văn bản này đã hết hiệu lực. Theo khảo sát của nhóm (Chương 2), hai hệ thống hỏi đáp pháp luật tiếng Việt gần nhất với đề tài không xét việc chọn phiên bản văn bản theo thời điểm sự việc, và hai bộ dữ liệu có công bố định dạng (Zalo AI 2021, ALQAC 2025) không kèm thời điểm này, nên chưa đánh giá được loại câu hỏi trên.

### 1.1.4. Hướng tiếp cận Agentic-RAG

RAG truy xuất một lượt có một số hạn chế: không phân biệt câu hỏi ngoài phạm vi, không biết khi nào bằng chứng chưa đủ, và không tự kiểm tra lại trích dẫn. Các công trình Corrective RAG (Yan và cộng sự, 2024) và Self-RAG (Asai và cộng sự, 2024) bổ sung bước tự đánh giá bằng chứng và tự phê bình đầu ra. Đề tài kế thừa ý tưởng này theo hướng **Agentic-RAG**: một tác tử tự định tuyến câu hỏi, tự đánh giá mức độ đầy đủ của bằng chứng, viết lại truy vấn khi cần, và tự kiểm chứng trích dẫn trước khi trả lời. Pham và cộng sự (2025) đã cho thấy hướng Agentic-RAG hiệu quả với pháp luật Việt Nam, nhưng chưa xét hiệu lực theo thời gian và chưa tách riêng đóng góp của từng thành phần tác tử.

## 1.2. Mục tiêu đề tài

### 1.2.1. Mục tiêu tổng quát

Đề tài xây dựng một hệ thống hỏi đáp pháp luật tiếng Việt hoàn chỉnh. Hệ thống tiếp nhận câu hỏi bằng ngôn ngữ tự nhiên, truy xuất căn cứ pháp lý từ kho văn bản có cấu trúc phân cấp, và sinh câu trả lời có trích dẫn đến cấp Điều, Khoản, **đúng phiên bản văn bản có hiệu lực tại thời điểm của tình huống**. Hệ thống được cung cấp qua giao diện web trực quan.

### 1.2.2. Mục tiêu cụ thể

1. **Kho dữ liệu có cấu trúc:** chuẩn hóa 5 văn bản thuộc 4 lĩnh vực (Dân sự, Lao động, Doanh nghiệp, Thương mại), phân đoạn theo cấu trúc Chương → Mục → Điều → Khoản, gắn siêu dữ liệu về khoảng hiệu lực.
2. **Truy xuất đa phương pháp:** cài đặt và so sánh BM25, tìm kiếm ngữ nghĩa (dense), tìm kiếm lai bằng Reciprocal Rank Fusion và xếp hạng lại bằng cross-encoder. Chỉ tiêu: Hit Rate@5 ≥ 80%, Recall@10 ≥ 75%.
3. **Tác tử Agentic-RAG có kiểm chứng trích dẫn:** đồ thị trạng thái gồm các bước định tuyến, truy xuất có lọc hiệu lực, đánh giá bằng chứng và viết lại truy vấn, sinh câu trả lời, kiểm chứng trích dẫn hai lớp. Chỉ tiêu: Citation Precision ≥ 85%. Hệ thống từ chối khi câu hỏi ngoài phạm vi hoặc không đủ căn cứ.
4. **Ứng dụng web:** giao diện NiceGUI gọi backend FastAPI. Người dùng bấm vào trích dẫn để đọc toàn văn điều luật và xem các bước tác tử đã thực hiện.
5. **Bộ dữ liệu kiểm thử và đánh giá:** 209 câu hỏi từ ba nguồn, trong đó có một tập giữ riêng 30 câu soạn sau khi đã cố định prompt; đo chất lượng truy xuất, trích dẫn, câu trả lời, độ đúng phiên bản và chi phí.

### 1.2.3. Câu hỏi nghiên cứu

Đề tài trả lời bốn câu hỏi nghiên cứu.

**RQ1 – Chiến lược truy xuất.** Kết hợp tìm kiếm từ khóa BM25 với tìm kiếm ngữ nghĩa bằng Reciprocal Rank Fusion, rồi xếp hạng lại bằng cross-encoder, cải thiện hiệu quả truy xuất căn cứ pháp lý tiếng Việt ở mức nào so với từng phương pháp đơn lẻ? Nhóm so sánh bốn cấu hình BM25, Dense, Hybrid và Hybrid kèm xếp hạng lại, theo các chỉ số Hit Rate@5, Recall@10 và MRR@10.

**RQ2 – Phân đoạn và cấu trúc phân cấp.** Phân đoạn theo cấu trúc pháp lý ảnh hưởng thế nào đến hiệu quả truy xuất và hiện tượng truy xuất nhầm văn bản (Document-Level Retrieval Mismatch, DRM; Reuter và cộng sự, 2025), so với phân đoạn cố định theo số từ? Nhóm so sánh bốn cách: phân đoạn cố định, theo Điều, theo Khoản, và theo Khoản có gắn tiêu đề phân cấp. Tất cả được đánh giá ở cấp Điều.

**RQ3 – Agentic-RAG.** Một tác tử biết tự định tuyến, tự đánh giá bằng chứng và tự kiểm chứng trích dẫn cải thiện chất lượng câu trả lời và độ chính xác trích dẫn ở mức nào so với RAG truy xuất một lượt, và với chi phí bao nhiêu? Nhóm thực hiện nghiên cứu lược bỏ (ablation): lần lượt tắt từng thành phần của tác tử rồi đo Citation Precision/Recall, Faithfulness, Answer Correctness, độ trễ và số lượt gọi LLM.

**RQ4 – Hiệu lực theo thời gian.** Khi kho dữ liệu chứa đồng thời văn bản còn hiệu lực và văn bản đã hết hiệu lực về cùng một vấn đề, hệ thống có trích dẫn đúng phiên bản văn bản có hiệu lực tại thời điểm xảy ra sự việc hay không? Nhóm so sánh ba chính sách: không lọc, chỉ lọc văn bản "còn hiệu lực", và lọc theo thời điểm sự việc do tác tử trích xuất từ câu hỏi.

## 1.3. Đối tượng và phạm vi nghiên cứu

### 1.3.1. Đối tượng nghiên cứu

Đối tượng nghiên cứu chính gồm ba thành phần: (1) quá trình truy xuất căn cứ pháp lý có xét đến cấu trúc phân cấp và hiệu lực theo thời gian của văn bản; (2) tác tử Agentic-RAG điều phối truy xuất và sinh câu trả lời; (3) cơ chế sinh và kiểm chứng trích dẫn.

### 1.3.2. Phạm vi dữ liệu

Kho dữ liệu gồm 5 văn bản luật:

| Mã | Văn bản | Số hiệu | Số Điều | Trạng thái |
|---|---|---|---|---|
| BLDS2015 | Bộ luật Dân sự 2015 | 91/2015/QH13 | 689 | Còn hiệu lực |
| BLLD2019 | Bộ luật Lao động 2019 | 45/2019/QH14 | 220 | Còn hiệu lực |
| LDN2020 | Luật Doanh nghiệp 2020 | 59/2020/QH14 | 218 | Còn hiệu lực |
| LTM2005 | Luật Thương mại 2005 | 36/2005/QH11 | 324 | Còn hiệu lực |
| BLLD2012 | Bộ luật Lao động 2012 | 10/2012/QH13 | 242 | Hết hiệu lực từ 01/01/2021 (chỉ dùng cho RQ4) |

Đơn vị truy xuất là Khoản, các Điểm nằm trong Khoản. Hệ thống đồng thời cho phép lấy toàn văn Điều chứa Khoản đó.

Tập kiểm thử gồm 209 câu hỏi từ ba nguồn, kết quả được báo cáo tách riêng theo nguồn:

- 77 câu do người viết, chọn lọc từ bộ Zalo AI Legal Text Retrieval 2021 (Zalo AI, 2021), gán nhãn cấp Điều.
- 65 câu tổng hợp (synthetic) sinh bằng LLM và kiểm định tay 20 câu.
- 67 câu nhóm tự soạn: 15 câu tình huống, 32 câu có mốc thời gian, 15 câu tra cứu trực tiếp và 5 câu ngoài phạm vi.

Trong 67 câu tự soạn, 30 câu (M_038–M_067: 20 câu có mốc thời gian, 10 câu tra cứu trực tiếp) là **tập giữ riêng**. Các câu này được soạn và chốt trước khi chạy hệ thống trên bất kỳ câu nào trong số đó, sau khi prompt của tác tử đã cố định. Vì prompt từng được chỉnh khi thấy lỗi trên các câu cũ, tập giữ riêng giúp kiểm tra rằng kết quả không chỉ "khớp" với những câu đã dùng để chỉnh (mục 5.1.1).

### 1.3.3. Giới hạn

- Không bao gồm Nghị định, Thông tư hướng dẫn, án lệ và bản án.
- Dùng văn bản gốc khi ban hành, chưa hợp nhất các lần sửa đổi, bổ sung (ví dụ các luật sửa đổi Luật Doanh nghiệp 2020).
- Hiệu lực được xử lý ở cấp văn bản; chưa xử lý việc từng Điều, Khoản bị sửa đổi.
- LLM dùng qua API miễn phí (Gemini, Groq). Embedding và reranker chạy cục bộ trên CPU. Không fine-tune mô hình.
- Hệ thống chỉ là công cụ tham khảo, không thay thế tư vấn của luật sư.

## 1.4. Phương pháp thực hiện

Đề tài thực hiện từ 15/08 đến 04/12/2026 theo mô hình Agile/Scrum rút gọn: sau giai đoạn khảo sát và đề cương (15/08–08/10), phần triển khai gồm 6 sprint từ 09/10 đến 27/11, tuần cuối dành cho rà soát và nộp. Hai thành viên phân công như sau: Phạm Huỳnh Quốc Đạt phụ trách lõi kỹ thuật (truy xuất, tác tử, API, đánh giá tự động); Hoàng Sinh Hùng phụ trách dữ liệu (kho văn bản, tập kiểm thử), giao diện và báo cáo. Về đánh giá:

- Các chỉ số truy xuất, trích dẫn và phiên bản được tính tự động bằng cách đối chiếu với nhãn chuẩn.
- Chất lượng câu trả lời được chấm bằng LLM-as-a-judge: Faithfulness theo định nghĩa của RAGAS (Es và cộng sự, 2024), Answer Correctness (so với đáp án mẫu) theo thư viện ragas. Bộ chấm được kiểm định bằng cách so với điểm chấm tay độc lập của một thành viên trên 20 câu trả lời (mục 5.1.4).

## 1.5. Đóng góp chính

1. **Kho văn bản pháp luật có cấu trúc kèm khoảng hiệu lực:** 5 văn bản được bóc tách thành cây Chương/Mục/Điều/Khoản/Điểm. Mỗi đoạn mang ngày có hiệu lực và ngày hết hiệu lực, trong đó có một văn bản đã hết hiệu lực để nghiên cứu hiệu lực theo thời gian.
2. **Truy xuất theo khoảng hiệu lực tại thời điểm của tình huống:** tác tử trích xuất thời điểm sự việc từ câu hỏi, rồi chỉ truy xuất văn bản có hiệu lực tại thời điểm đó. Hiệu quả được đo bằng tỷ lệ trích đúng phiên bản (RQ4).
3. **Tác tử Agentic-RAG có kiểm chứng trích dẫn hai lớp:** lớp thứ nhất đối chiếu mã trích dẫn với ngữ cảnh; lớp thứ hai dùng LLM kiểm tra từng cặp (khẳng định, đoạn luật). Tác tử từ chối khi ngoài phạm vi hoặc không đủ căn cứ.
4. **Đánh giá tách riêng từng thành phần:** nghiên cứu lược bỏ trên 5 cấu hình (baseline, full, no_router, no_grading, no_verify), báo cáo cả chất lượng lẫn chi phí (độ trễ, số lượt gọi LLM).
5. **Bộ kiểm thử ba nguồn** có nhãn căn cứ chuẩn và **ứng dụng web** hiển thị trích dẫn bấm được cùng các bước của tác tử.

## 1.6. Bố cục báo cáo

- **Chương 1 – Tổng quan đề tài:** đặt vấn đề, mục tiêu, câu hỏi nghiên cứu, phạm vi và đóng góp.
- **Chương 2 – Tổng quan tài liệu:** các nghiên cứu liên quan trên thế giới và trong nước, vấn đề còn tồn tại và hướng tiếp cận của đề tài.
- **Chương 3 – Cơ sở lý thuyết:** BM25, truy xuất dày đặc, RRF, cross-encoder, RAG, Agentic-RAG, LangGraph và đặc thù văn bản pháp luật Việt Nam.
- **Chương 4 – Phân tích và thiết kế hệ thống:** kiến trúc tổng thể, pipeline dữ liệu, động cơ truy xuất, tác tử, API và giao diện.
- **Chương 5 – Thực nghiệm và đánh giá:** tập kiểm thử, các chỉ số, kết quả RQ1–RQ4 và phân tích lỗi.
- **Chương 6 – Kết luận và hướng phát triển:** kết quả đạt được, hạn chế và hướng mở rộng.

