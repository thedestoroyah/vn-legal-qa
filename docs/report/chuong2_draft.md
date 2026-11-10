# CHƯƠNG 2. TỔNG QUAN TÀI LIỆU

> **Bản nháp** — Đạt, 10/11/2026. Mở rộng từ mục 7 đề cương. Chỉ dùng tài liệu ở mục 12 đề cương (đã tra lại nguồn ngày 03/11; ALQAC 2025 tra và thêm ngày 10/11).
> Chương này nói công trình nào đã làm gì, đề tài kế thừa gì và còn thiếu gì. Cơ chế kỹ thuật của từng phương pháp (BM25, BGE-M3, RRF, cross-encoder, RAG, Agentic-RAG, DRM, lọc hiệu lực) trình bày ở Chương 3, không lặp lại ở đây.

Nhóm khảo sát các nghiên cứu liên quan theo bốn hướng: (1) truy xuất văn bản pháp luật; (2) dữ liệu và hệ thống hỏi đáp pháp luật tiếng Việt; (3) RAG có tự đánh giá và Agentic-RAG; (4) trích dẫn và đánh giá câu trả lời. Cuối chương tổng hợp các vấn đề còn tồn tại và nêu hướng tiếp cận của đề tài cho từng vấn đề.

## 2.1. Truy xuất văn bản pháp luật

### 2.1.1. Đánh giá riêng bước truy xuất

Trong một hệ thống RAG, câu trả lời chỉ tốt khi đoạn văn bản được truy xuất đúng. LegalBench-RAG (Pipitone & Houir Alami, 2024) là bộ đánh giá dành riêng cho bước truy xuất trong RAG pháp luật. Bộ này yêu cầu hệ thống tìm đúng đoạn văn bản tối thiểu làm căn cứ, thay vì chỉ tìm đúng cả văn bản, vì một văn bản luật dài có thể chứa nhiều quy định không liên quan đến câu hỏi.

Đề tài theo hướng này ở hai điểm: chọn Khoản làm đơn vị truy xuất, và đánh giá truy xuất độc lập với bước sinh câu trả lời (RQ1, RQ2) trước khi đánh giá cả tác tử (RQ3, RQ4).

### 2.1.2. Truy xuất nhầm văn bản

Reuter và cộng sự (2025) chỉ ra rằng trong kho văn bản pháp luật lớn, nhiều văn bản có cấu trúc và cách diễn đạt tương tự nhau, nên hệ thống dễ lấy đoạn văn từ sai văn bản nguồn. Nhóm tác giả gọi hiện tượng này là Document-Level Retrieval Mismatch (DRM) và đề xuất Summary-Augmented Chunking: gắn thêm bản tóm tắt cấp văn bản vào từng đoạn để đoạn đó mang ngữ cảnh của văn bản chứa nó.

Đề tài áp dụng ý tưởng này ở dạng gọn hơn: thay bản tóm tắt bằng tiêu đề phân cấp (tên văn bản, số và tên Điều) gắn vào từng đoạn (mục 3.8.1, 4.2.3), và đo tỷ lệ đoạn thuộc văn bản không có trong căn cứ chuẩn (DRM@5) ở RQ2. Các câu của RQ2 không nêu thời điểm sự việc nên chỉ được truy xuất trên 4 văn bản còn hiệu lực; DRM@5 vì vậy đo việc lấy nhầm giữa các văn bản khác lĩnh vực. Kho của đề tài còn có một dạng nhầm khó hơn: Bộ luật Lao động 2012 và 2019 điều chỉnh cùng các vấn đề, nhiều Điều có nội dung gần giống nhau, nên lấy nhầm văn bản lúc này đồng nghĩa với trích sai phiên bản. Dạng nhầm này được đo bằng tỷ lệ đúng phiên bản ở RQ3 và RQ4.

## 2.2. Tình hình nghiên cứu trong nước

### 2.2.1. Dữ liệu và cuộc thi

- **Zalo AI Challenge 2021 – Legal Text Retrieval** (Zalo AI, 2021) cung cấp khoảng 3.200 câu hỏi do người viết, mỗi câu gắn với các điều luật liên quan; dữ liệu được công bố lại theo giấy phép MIT. Đây là nguồn câu hỏi thực tế chính của đề tài cho thực nghiệm truy xuất: nhóm chọn các câu thuộc phạm vi 5 văn bản trong kho (mục 5.1.1).
- **ALQAC** (Automated Legal Question Answering Competition) được tổ chức hằng năm cùng hội nghị KSE từ năm 2021. Lần thứ năm (ALQAC 2025) gồm hai nhiệm vụ trên văn bản luật tiếng Việt: truy xuất văn bản pháp luật và hỏi đáp pháp luật; năm này bổ sung bài toán dạng tình huống và dữ liệu huấn luyện gồm cả phần được chuyên gia kiểm tra và phần chưa được kiểm tra (Do và cộng sự, 2025).
- **VLQA** (Nguyen và cộng sự, 2025) gồm 3.129 bộ (câu hỏi, điều luật liên quan, câu trả lời) do chuyên gia gán nhãn trên 59.636 điều luật thuộc 27 lĩnh vực. Câu hỏi được thu thập từ các nền tảng tư vấn pháp luật công khai nên phản ánh nhu cầu thực tế của người dân. Bộ này cũng là dữ liệu của nhiệm vụ DRiLL tại VLSP 2025. Khi nhóm kiểm tra (15/10/2026), dữ liệu VLQA chưa được công bố nên không dùng được trong đề tài.

Điểm chung của các bộ dữ liệu trên là mỗi câu hỏi gắn với một tập điều luật chuẩn, xác định theo số hiệu văn bản. Trong định dạng dữ liệu công bố của Zalo AI 2021 và ALQAC 2025, câu hỏi không kèm thời điểm xảy ra sự việc. Vì vậy, các bộ này đo được việc tìm đúng điều luật, nhưng không đo được việc chọn đúng phiên bản văn bản khi quy định thay đổi theo thời gian.

### 2.2.2. Hệ thống hỏi đáp pháp luật tiếng Việt

- **Nguyen Ba và cộng sự (2024)** (báo cáo môn học, đăng trên arXiv) xây dựng hệ thống hỏi đáp pháp luật tiếng Việt gồm: LLM viết lại câu hỏi, kết hợp tìm kiếm từ khóa và tìm kiếm vector bằng một biến thể chuẩn hóa của Reciprocal Rank Fusion, LLM sinh câu trả lời từ các Điều truy xuất được, rồi xếp hạng lại các đoạn bằng điểm BM25 và vector so với chính câu trả lời đó; nhóm tác giả đề xuất cách này để thay cho cross-encoder. Thực nghiệm so sánh từng thành phần truy xuất (BM25, bi-encoder, tìm kiếm lai, xếp hạng lại dựa trên câu trả lời của LLM) theo Recall@k và MAP@k trên dữ liệu Zalo và dữ liệu tự thu thập. Đề tài kế thừa hướng kết hợp hai cách tìm kiếm bằng RRF và cách so sánh từng thành phần ở RQ1; khác ở bước xếp hạng lại (dùng cross-encoder, trước khi sinh) và ở việc đánh giá cả trích dẫn lẫn câu trả lời, không chỉ truy xuất.
- **Pham và cộng sự (2025)** xây dựng chatbot tư vấn pháp luật dựa trên Agentic-RAG: một Router Agent điều phối các tác tử chuyên biệt và nhiều công cụ (tìm kiếm vector, cơ sở dữ liệu đồ thị, tìm kiếm web) trên khoảng 54.000 văn bản. Trên 1.247 câu hỏi thực tế, hệ thống đạt độ chính xác 82,3%, context precision và context recall cao hơn hệ thống cơ sở lần lượt 17,2% và 29,7%. Đây là công trình gần nhất với định hướng của đề tài. Bài báo có đo độ chính xác trích dẫn (Legal Citation Accuracy), nhưng theo nghĩa trích dẫn có đúng chuẩn trình bày trích dẫn pháp luật Việt Nam hay không, không kiểm điều luật được trích có hỗ trợ nội dung câu trả lời hay không. Ở bước tiền xử lý, nhóm tác giả loại các quy định đã bị thay thế khỏi dữ liệu, tức hệ thống chỉ làm việc với văn bản hiện hành, tương ứng với chính sách `current` mà đề tài so sánh ở RQ4. Hệ thống được so với các hệ thống cơ sở (RAG truyền thống, RAG một tác tử, tìm kiếm pháp luật truyền thống, chatbot thương mại); bài không trình bày đánh giá riêng từng tác tử.

## 2.3. RAG có tự đánh giá và Agentic-RAG

RAG (Lewis và cộng sự, 2020) kết hợp mô hình sinh với một bộ truy xuất trên kho tri thức bên ngoài, để câu trả lời dựa vào văn bản được truy xuất thay vì chỉ dựa vào tri thức mô hình đã học. Ở dạng cơ bản, RAG truy xuất một lượt rồi sinh, nên khi truy xuất sai thì câu trả lời sai theo (mục 3.5.2).

Hai công trình bổ sung bước tự đánh giá vào RAG:

- **Corrective RAG** (Yan và cộng sự, 2024) thêm một bộ đánh giá chất lượng tài liệu truy xuất; khi bằng chứng không đủ tin cậy, hệ thống tinh lọc lại tri thức trong tài liệu hoặc bổ sung bằng tìm kiếm web.
- **Self-RAG** (Asai và cộng sự, 2024) huấn luyện mô hình sinh các token phản tỉnh để tự quyết định khi nào cần truy xuất và tự phê bình đầu ra.

Đề tài kế thừa hai ý tưởng này cho bước đánh giá bằng chứng, viết lại truy vấn và kiểm chứng của tác tử. Khác với Self-RAG, đề tài không huấn luyện lại mô hình mà hiện thực các bước bằng prompt trên một đồ thị trạng thái (mục 3.6, 3.7). Cách làm này cho phép bật, tắt từng bước bằng cờ cấu hình để đo riêng đóng góp của từng bước (mục 4.4.3).

## 2.4. Trích dẫn và đánh giá câu trả lời

- **ALCE** (Gao và cộng sự, 2023) đề xuất khung đánh giá khả năng sinh văn bản kèm trích dẫn của LLM, với hai chỉ số citation recall và citation precision. Kết quả của ALCE cho thấy ngay cả các mô hình mạnh vẫn thường đưa ra trích dẫn không hỗ trợ cho khẳng định đi kèm. Với văn bản pháp luật, trích dẫn là thứ người đọc dùng để tự kiểm tra câu trả lời, nên một trích dẫn sai nguy hiểm hơn một câu trả lời thiếu ý.
- **RAGAS** (Es và cộng sự, 2024) đề xuất chấm hệ thống RAG bằng LLM mà không cần nhãn chuẩn, với các chỉ số Faithfulness (câu trả lời có bám vào ngữ cảnh không), Answer Relevance và Context Relevance. Chỉ số Answer Correctness (câu trả lời có đúng so với đáp án mẫu không) có trong thư viện ragas đi kèm và cần đáp án mẫu.

Đề tài dùng định nghĩa của hai khung này, điều chỉnh cho bài toán và giới hạn API miễn phí: citation precision và recall tính ở cấp Điều bằng cách đối chiếu với căn cứ chuẩn (tính bằng code, không cần LLM); Faithfulness và Answer Correctness chấm bằng một mô hình của nhà cung cấp khác với mô hình của tác tử, mỗi câu trả lời một lượt, và được đối chiếu với chấm tay (mục 5.1.4).

## 2.5. Tổng hợp vấn đề tồn tại và hướng tiếp cận

### 2.5.1. Tổng hợp các công trình

**Bảng 2.1.** Các công trình liên quan và mối liên hệ với đề tài.

| Công trình | Đóng góp chính | Đề tài kế thừa | Đề tài bổ sung |
|---|---|---|---|
| Zalo AI (2021) | Câu hỏi thực tế kèm điều luật chuẩn | Nguồn câu hỏi cho RQ1, RQ2 | Câu hỏi có mốc thời gian, có đáp án mẫu |
| Do và cộng sự (2025), ALQAC 2025 | Cuộc thi truy xuất và hỏi đáp trên luật tiếng Việt | Cách đặt bài toán theo điều luật chuẩn | Đánh giá đúng phiên bản theo thời gian |
| Nguyen và cộng sự (2025), VLQA | Bộ dữ liệu lớn do chuyên gia gán nhãn | (chưa công bố khi thực hiện) | – |
| Nguyen Ba và cộng sự (2024) | Truy xuất lai + RRF chuẩn hóa, xếp hạng lại dựa trên câu trả lời của LLM | Truy xuất lai + RRF; so sánh từng thành phần truy xuất | Xếp hạng lại bằng cross-encoder; đánh giá trích dẫn và câu trả lời |
| Pham và cộng sự (2025) | Agentic-RAG với Router Agent cho luật Việt Nam | Ý tưởng bộ định tuyến | Lọc theo hiệu lực thay vì bỏ văn bản cũ; kiểm trích dẫn có hỗ trợ câu trả lời; đánh giá lược bỏ từng thành phần |
| Yan và cộng sự (2024); Asai và cộng sự (2024) | Tự đánh giá bằng chứng, tự phê bình đầu ra | Bước grade, viết lại truy vấn | Hiện thực bằng prompt, đo riêng từng bước |
| Pipitone & Houir Alami (2024) | Đánh giá riêng bước truy xuất, đoạn tối thiểu | Khoản làm đơn vị; đánh giá truy xuất độc lập | – |
| Reuter và cộng sự (2025) | Hiện tượng DRM, gắn ngữ cảnh văn bản vào đoạn | Gắn tiêu đề phân cấp | Đo DRM@5 trên luật Việt Nam; đo nhầm phiên bản riêng bằng tỷ lệ đúng phiên bản |
| Gao và cộng sự (2023); Es và cộng sự (2024) | Chỉ số trích dẫn; chỉ số chấm bằng LLM | Định nghĩa chỉ số | Kiểm chứng trích dẫn sau khi sinh; phép thử tiêm trích dẫn sai |

### 2.5.2. Vấn đề tồn tại

Theo khảo sát của nhóm, có bốn vấn đề chưa được giải quyết đầy đủ:

1. **Chưa xét hiệu lực theo thời gian.** Hai hệ thống hỏi đáp pháp luật tiếng Việt nêu trên không xét việc chọn phiên bản văn bản theo thời điểm xảy ra sự việc; Pham và cộng sự (2025) còn loại hẳn các quy định đã bị thay thế khỏi dữ liệu. Trong khi đó, nhiều câu hỏi thực tế liên quan đến sự việc xảy ra khi một văn bản khác đang có hiệu lực (mục 1.1.3). Các bộ dữ liệu công bố cũng không kèm thời điểm sự việc (mục 2.2.1), nên chưa có cách đo việc trích đúng phiên bản.
2. **Đánh giá tác tử ở mức tổng thể.** Với pháp luật Việt Nam, hệ thống Agentic-RAG gần nhất (Pham và cộng sự, 2025) được so sánh tổng thể với các hệ thống cơ sở, không tách riêng đóng góp của từng thành phần (định tuyến, đánh giá bằng chứng, kiểm chứng trích dẫn) và chi phí tương ứng (số lượt gọi LLM, độ trễ). Khi không tách riêng, khó biết thành phần nào đáng giữ khi tài nguyên bị giới hạn.
3. **Trích dẫn chưa được kiểm chứng và đo riêng.** ALCE cho thấy LLM thường sinh trích dẫn không hỗ trợ cho khẳng định. Nguyen Ba và cộng sự (2024) chỉ đánh giá bước truy xuất; Pham và cộng sự (2025) đo độ chính xác trích dẫn theo nghĩa đúng chuẩn trình bày. Hai công trình này chưa kiểm tra điều luật được trích có thực sự hỗ trợ khẳng định đi kèm hay không, trong khi đây là loại lỗi ALCE chỉ ra là phổ biến.
4. **Nhầm văn bản khi kho có nhiều văn bản giống nhau.** Hiện tượng DRM (Reuter và cộng sự, 2025) nặng hơn khi kho chứa hai phiên bản của cùng một bộ luật: nhầm văn bản lúc này đồng nghĩa với trích sai phiên bản.

### 2.5.3. Hướng tiếp cận của đề tài

**Bảng 2.2.** Vấn đề tồn tại, giải pháp và câu hỏi nghiên cứu tương ứng.

| Vấn đề | Giải pháp của đề tài | Câu hỏi nghiên cứu | Trình bày ở |
|---|---|---|---|
| 1. Hiệu lực theo thời gian | Gắn khoảng hiệu lực cho từng văn bản; bộ định tuyến trích ngày sự việc từ câu hỏi; chỉ truy xuất văn bản có hiệu lực tại ngày đó; soạn câu hỏi có mốc thời gian và đo tỷ lệ đúng phiên bản | RQ4 (và router trong RQ3) | mục 3.8.2, 4.3, 5.5 |
| 2. Đánh giá tổng thể | Một đồ thị dùng chung cho 5 cấu hình, bật/tắt từng thành phần bằng cờ; so sánh ghép cặp theo câu, khoảng tin cậy bootstrap; đo cả độ trễ và số lượt LLM | RQ3 | mục 4.4.3, 5.4 |
| 3. Trích dẫn | Kiểm chứng trích dẫn hai lớp sau khi sinh; citation precision/recall cấp Điều tính bằng code; phép thử tiêm trích dẫn sai | RQ3 | mục 4.4.2, 5.4.3 |
| 4. Nhầm văn bản | Phân đoạn theo cấu trúc luật, gắn tiêu đề phân cấp vào đoạn; đo DRM@5; nhầm phiên bản đo bằng tỷ lệ đúng phiên bản (RQ3, RQ4) | RQ2 (và RQ1 cho phương pháp truy xuất) | mục 3.8.1, 5.2, 5.3 |

Như vậy, đề tài không đề xuất mô hình truy xuất hay mô hình ngôn ngữ mới. Đóng góp nằm ở việc đưa hiệu lực theo thời gian vào truy xuất và đánh giá, và ở việc đo riêng từng thành phần của tác tử trên dữ liệu pháp luật Việt Nam. Chương 3 trình bày cơ sở lý thuyết của các phương pháp được dùng; Chương 4 trình bày thiết kế hệ thống; Chương 5 trình bày kết quả thực nghiệm cho từng câu hỏi nghiên cứu.
