# ĐỀ CƯƠNG CÔNG TRÌNH DỰ ÁN CÔNG NGHỆ THÔNG TIN

**NĂM HỌC 2026 – 2027**

## 0. Thành viên

- Phạm Huỳnh Quốc Đạt - 52300098
- Hoàng Sinh Hùng - 52300106

## 1. Tên đề tài

- Tiếng Việt: Phát triển hệ thống hỏi đáp pháp luật Việt Nam dựa trên Agentic-RAG với truy xuất căn cứ theo hiệu lực và kiểm chứng trích dẫn.
- Tiếng Anh: Developing a Vietnamese Legal Question Answering System based on Agentic-RAG with Temporally-Aware Legal Retrieval and Citation Verification.

## 2. Lý do chọn đề tài

1. Pháp luật Việt Nam được thể hiện qua một khối lượng lớn văn bản với cấu trúc phân cấp như văn bản, chương, mục, điều, khoản và điểm; đồng thời giữa các văn bản tồn tại nhiều quan hệ như sửa đổi, bổ sung, thay thế và dẫn chiếu. Điều này khiến việc tìm kiếm và xác định đúng cơ sở pháp lý cho một câu hỏi cụ thể trở nên khó khăn khi chỉ sử dụng phương pháp tìm kiếm từ khóa thông thường.
2. Sự phát triển của các mô hình ngôn ngữ lớn (LLMs) và Retrieval-Augmented Generation (RAG) tạo điều kiện xây dựng các hệ thống hỏi đáp có khả năng kết hợp truy xuất thông tin pháp lý với sinh câu trả lời bằng ngôn ngữ tự nhiên. Tuy nhiên, trong lĩnh vực pháp luật, một câu trả lời không chỉ cần phù hợp về nội dung mà còn cần dựa trên cơ sở pháp lý phù hợp và chỉ ra được nguồn trích dẫn, nhằm giúp người sử dụng có thể kiểm tra lại thông tin.
3. Vì vậy, đề tài hướng đến việc phát triển một hệ thống hỏi đáp pháp luật tiếng Việt có khả năng tiếp nhận câu hỏi bằng tiếng Việt, truy xuất các cơ sở pháp lý liên quan từ kho văn bản pháp luật và tạo câu trả lời kèm trích dẫn. Hệ thống đồng thời xem xét các đặc trưng của văn bản pháp luật Việt Nam, đặc biệt là cấu trúc phân cấp và hiệu lực theo thời gian: cùng một vấn đề có thể được điều chỉnh bởi các văn bản khác nhau tùy thời điểm xảy ra tình huống, nên câu trả lời đúng phải dựa trên văn bản có hiệu lực tại thời điểm đó.
4. Ngoài ra, mô hình ngôn ngữ lớn có xu hướng sinh trích dẫn không chính xác hoặc không hỗ trợ cho khẳng định. Đề tài vì vậy tiếp cận theo hướng Agentic-RAG: thay vì truy xuất một lượt, tác tử tự định tuyến câu hỏi, tự đánh giá mức độ đầy đủ của bằng chứng, truy xuất lại khi cần và tự kiểm chứng trích dẫn trước khi trả lời.

## 3. Mục tiêu nghiên cứu

### 3.1. Mục tiêu tổng quát

Xây dựng một hệ thống phần mềm hỏi đáp pháp luật tiếng Việt hoàn chỉnh (End-to-End System) có khả năng tiếp nhận câu hỏi bằng ngôn ngữ tự nhiên, tự động định tuyến và truy xuất chính xác các căn cứ pháp lý liên quan từ kho văn bản quy phạm pháp luật phân cấp, đồng thời sinh câu trả lời giải thích tự nhiên có đính kèm trích dẫn nguồn luật minh bạch (đến cấp Điều, Khoản) đúng phiên bản văn bản có hiệu lực tại thời điểm của tình huống, trên giao diện ứng dụng trực quan.

### 3.2. Mục tiêu cụ thể

1. **Xây dựng và chuẩn hóa kho dữ liệu pháp luật có cấu trúc (ETL & Structured Knowledge Base):**
  - Thu thập, làm sạch và chuẩn hóa văn bản quy phạm pháp luật thuộc các lĩnh vực trọng tâm (Dân sự, Lao động, Doanh nghiệp, Thương mại), bao gồm cả một văn bản đã hết hiệu lực (Bộ luật Lao động 2012) phục vụ nghiên cứu hiệu lực theo thời gian.
  - Phân đoạn văn bản đệ quy (Recursive Chunking) bảo toàn cấu trúc logic phân cấp: Văn bản → Chương → Mục → Điều → Khoản → Điểm, tích hợp siêu dữ liệu (số hiệu, ngày ban hành, ngày có hiệu lực, ngày hết hiệu lực, trạng thái hiệu lực) phục vụ việc lọc theo thời điểm và truy vấn chính xác.
2. **Thiết kế và tối ưu hóa Pipeline Truy xuất Đa phương pháp (Retrieval Engine Optimization):**
  - Cài đặt và thực nghiệm so sánh các kỹ thuật tìm kiếm: Tìm kiếm từ khóa thưa (Sparse Retrieval - BM25), Tìm kiếm ngữ nghĩa dày (Dense Retrieval - Vector Embeddings), Tìm kiếm lai (Hybrid Search) và xếp hạng lại (Cross-Encoder Reranking).
  - Đạt các chỉ số truy xuất mục tiêu trên tập kiểm thử: Hit Rate@5 ≥ 80% và Recall@10 ≥ 75% đối với các đoạn văn bản chứa căn cứ pháp lý cần thiết.
3. **Xây dựng Tác tử Agentic-RAG có kiểm chứng trích dẫn (Agentic-RAG with Citation Verification):**
  - Thiết kế tác tử dạng đồ thị trạng thái (LangGraph) gồm các bước: định tuyến câu hỏi (phân loại câu hỏi tình huống / tra cứu trực tiếp điều luật / ngoài phạm vi và trích xuất thời điểm của tình huống), truy xuất có lọc theo khoảng hiệu lực, tự đánh giá mức độ đầy đủ của bằng chứng và viết lại truy vấn (tối đa 2 vòng), sinh câu trả lời có gắn trích dẫn, và tự kiểm chứng trích dẫn.
  - Kiểm chứng trích dẫn hai lớp: (1) đối chiếu mã trích dẫn với các đoạn đã đưa vào ngữ cảnh; (2) dùng LLM kiểm tra từng khẳng định có được đoạn luật được trích hỗ trợ hay không, loại bỏ trích dẫn không đạt và sinh lại khi cần. Mục tiêu Citation Precision ≥ 85%.
  - Hệ thống từ chối trả lời khi câu hỏi ngoài phạm vi hoặc không tìm đủ căn cứ, thay vì sinh câu trả lời không có căn cứ.
4. **Phát triển Ứng dụng Hoàn chỉnh (Interactive Web Application):**
  - Xây dựng giao diện web trực quan (Streamlit, gọi backend FastAPI) cho phép người dùng nhập câu hỏi pháp luật, xem câu trả lời được giải thích rõ ràng, nhấp trực tiếp vào các trích dẫn để đọc toàn văn điều luật gốc, và xem vết thực thi các bước tác tử đã thực hiện.
5. **Xây dựng Bộ dữ liệu Kiểm thử và Đánh giá Hiệu năng Hệ thống (Evaluation Benchmark):**
  - Xây dựng tập kiểm thử khoảng 170–180 câu hỏi pháp luật có căn cứ điều luật chuẩn, từ ba nguồn được báo cáo tách riêng: (1) khoảng 80 câu do người viết, chọn lọc từ bộ Zalo AI Legal Text Retrieval 2021 (thuộc Bộ luật Dân sự và Luật Doanh nghiệp, gán nhãn ở cấp Điều); (2) 65 câu tổng hợp (synthetic) do nhóm sinh bằng LLM và kiểm tra, phủ cả 4 lĩnh vực, có câu trả lời mẫu; (3) khoảng 30–35 câu nhóm tự soạn, gồm câu tình huống cho Bộ luật Lao động và Luật Thương mại, câu có mốc thời gian (10–15), câu tra cứu trực tiếp điều luật (~5) và câu ngoài phạm vi (~5).
  - Đo lường toàn diện hiệu năng của hệ thống qua các bộ chỉ số: hiệu quả truy xuất (Hit Rate@5, Recall@10, MRR@10, tỷ lệ DRM), chất lượng câu trả lời (Faithfulness, Answer Correctness), độ chính xác trích dẫn (Citation Precision/Recall), độ đúng phiên bản văn bản theo thời điểm, tỷ lệ từ chối đúng câu hỏi ngoài phạm vi, độ trễ và số lượt gọi LLM.

## 4. Đối tượng nghiên cứu

### 4.1. Đối tượng nghiên cứu chính

Đối tượng nghiên cứu chính của Dự án tập trung vào ba thành phần cốt lõi: (1) quá trình truy xuất cơ sở pháp lý có xét đến cấu trúc phân cấp và hiệu lực theo thời gian của văn bản; (2) tác tử Agentic-RAG điều phối truy xuất và sinh câu trả lời; (3) cơ chế sinh và kiểm chứng trích dẫn.

### 4.2. Các thành phần được nghiên cứu

- Dữ liệu: văn bản pháp luật Việt Nam và các thông tin liên quan đến văn bản.
- Câu hỏi: câu hỏi pháp luật bằng tiếng Việt.
- Phương pháp truy xuất: sparse, dense, hybrid retrieval và/hoặc reranking.
- Phương pháp sinh: RAG và Agentic-RAG.
- Cơ sở pháp lý: văn bản, điều, khoản, điểm hoặc đoạn văn bản được truy xuất.
- Thông tin cấu trúc: quan hệ phân cấp giữa các thành phần của văn bản.
- Thông tin hiệu lực: khoảng thời gian hiệu lực của văn bản (ngày có hiệu lực, ngày hết hiệu lực) và thời điểm xảy ra tình huống trong câu hỏi.
- Trích dẫn: liên kết giữa câu trả lời và nguồn/cơ sở pháp lý được sử dụng.

---

### 4.3. Đối tượng sử dụng dự kiến

Hệ thống hướng tới phục vụ đa dạng các nhóm người dùng có nhu cầu tra cứu và tìm hiểu thông tin pháp luật Việt Nam, chẳng hạn như: sinh viên, người lao động, người dân có nhu cầu tìm kiếm thông tin pháp luật,…

## 5. Ý nghĩa đề tài

### 5.1. Ý nghĩa khoa học

- Khảo sát và đánh giá khả năng áp dụng các kỹ thuật Information Retrieval, Retrieval-Augmented Generation (RAG) và Agentic-RAG cho bài toán hỏi đáp pháp luật tiếng Việt.
- Nghiên cứu ảnh hưởng của các đặc trưng riêng của văn bản pháp luật Việt Nam, như cấu trúc phân cấp và hiệu lực theo thời gian, đối với quá trình truy xuất cơ sở pháp lý và sinh câu trả lời; đề xuất cơ chế truy xuất theo khoảng hiệu lực tại thời điểm của tình huống.
- Đo lường định lượng đóng góp riêng của từng thành phần tác tử (định tuyến, đánh giá bằng chứng và viết lại truy vấn, kiểm chứng trích dẫn) cùng chi phí tương ứng thông qua nghiên cứu lược bỏ (ablation study).
- Xây dựng phương pháp đánh giá hệ thống không chỉ dựa trên chất lượng câu trả lời mà còn xem xét chất lượng truy xuất bằng chứng, độ chính xác của trích dẫn và độ đúng phiên bản văn bản theo thời điểm.

### 5.2. Ý nghĩa thực tiễn

- Hỗ trợ người dùng tìm kiếm và tiếp cận các quy định pháp luật Việt Nam thông qua ngôn ngữ tự nhiên thay vì phải tự tìm kiếm trong nhiều văn bản.
- Cung cấp câu trả lời kèm cơ sở/trích dẫn pháp lý để người dùng có thể kiểm tra lại nguồn thông tin.
- Tạo nền tảng có thể tiếp tục phát triển thành các hệ thống hỗ trợ tra cứu pháp luật tiếng Việt với khả năng xử lý tốt hơn các quan hệ giữa các văn bản và các thay đổi về hiệu lực pháp lý.

## 6. Câu hỏi nghiên cứu

- **RQ1 (Về Chiến lược Truy xuất - Retrieval Strategy):**
  - Việc kết hợp tìm kiếm từ khóa (BM25), tìm kiếm ngữ nghĩa (Dense Vector Search) bằng Reciprocal Rank Fusion và mô hình xếp hạng lại (Cross-Encoder Reranker) cải thiện hiệu quả truy xuất căn cứ pháp lý tiếng Việt ở mức nào so với từng phương pháp đơn lẻ?
  - Thực nghiệm: so sánh BM25 / Dense / Hybrid (RRF) / Hybrid + Reranker.
  - Chỉ số: Hit Rate@5, Recall@10, MRR@10.
- **RQ2 (Về Tổ chức Dữ liệu & Cấu trúc Phân cấp - Chunking & Hierarchy):**
  - Cách phân đoạn văn bản theo cấu trúc pháp lý (Chương → Mục → Điều → Khoản) ảnh hưởng như thế nào đến hiệu quả truy xuất và hiện tượng truy xuất nhầm văn bản (Document-Level Retrieval Mismatch - DRM) so với phân đoạn cố định theo số lượng từ?
  - Thực nghiệm: so sánh Fixed-size Chunking / Chunk theo Điều (kèm tiêu đề phân cấp) / Chunk theo Khoản / Chunk theo Khoản kèm tiêu đề phân cấp (tên văn bản, Điều, tên Điều); các phương pháp được so ở cấp Điều. Việc mở rộng ngữ cảnh từ Khoản lên Điều cha được dùng ở bước sinh câu trả lời của tác tử, không thuộc thực nghiệm truy xuất.
  - Chỉ số: Hit Rate@5, Recall@10, tỷ lệ DRM (tỷ lệ đoạn trong top-k thuộc sai văn bản luật).
- **RQ3 (Về Agentic-RAG - Agentic Retrieval & Citation Verification):**
  - Một tác tử (agent) có khả năng tự định tuyến câu hỏi, tự đánh giá mức độ đầy đủ của bằng chứng để viết lại truy vấn, và tự kiểm chứng trích dẫn sau khi sinh câu trả lời cải thiện chất lượng câu trả lời và độ chính xác trích dẫn ở mức nào so với RAG truy xuất một lượt, và với chi phí (độ trễ, số lượt gọi LLM) ra sao?
  - Thực nghiệm: so sánh RAG một lượt / Agentic-RAG đầy đủ / Agentic-RAG lần lượt lược bỏ từng thành phần (bộ định tuyến, vòng viết lại truy vấn, bước kiểm chứng trích dẫn) (ablation study).
  - Chỉ số: Citation Precision, Citation Recall, Faithfulness, Answer Correctness, độ trễ (Latency), số lượt gọi LLM trên mỗi câu hỏi.
- **RQ4 (Về Hiệu lực Pháp luật theo Thời gian - Temporal Validity):**
  - Hệ thống có xác định và trích dẫn đúng phiên bản văn bản pháp luật có hiệu lực tại thời điểm xảy ra tình huống được hỏi hay không, khi kho dữ liệu chứa đồng thời văn bản còn hiệu lực và văn bản đã hết hiệu lực điều chỉnh cùng một vấn đề?
  - Thực nghiệm: kho dữ liệu bổ sung Bộ luật Lao động 2012 (hết hiệu lực từ 01/01/2021) bên cạnh Bộ luật Lao động 2019; tập 10–15 câu hỏi có mốc thời gian cụ thể; so sánh không lọc hiệu lực / lọc theo trạng thái "còn hiệu lực" / agent trích xuất thời điểm của tình huống và lọc theo khoảng hiệu lực của văn bản.
  - Chỉ số: tỷ lệ trích dẫn đúng phiên bản văn bản pháp luật.

## 7. Tổng quan tài liệu - Nghiên cứu liên quan

Nhóm khảo sát các nghiên cứu liên quan trực tiếp đến bài toán theo bốn hướng: truy xuất văn bản pháp luật tiếng Việt, RAG và Agentic-RAG, đặc trưng của dữ liệu pháp luật, và trích dẫn cùng phương pháp đánh giá. Kết quả khảo sát là cơ sở để lựa chọn phương pháp và thiết kế kiến trúc hệ thống.

- **Truy xuất văn bản pháp luật tiếng Việt:**
  - Nguyen Ba và cộng sự (2024) xây dựng pipeline truy xuất cho hệ thống hỏi đáp pháp luật tiếng Việt, kết hợp tìm kiếm từ khóa và tìm kiếm vector bằng một biến thể chuẩn hóa của Reciprocal Rank Fusion; sau khi LLM sinh câu trả lời, các đoạn được xếp hạng lại dựa trên chính câu trả lời đó (nhóm tác giả đề xuất cách này thay cho cross-encoder). Kỹ thuật RRF (Cormack và cộng sự, 2009) và mô hình embedding đa ngôn ngữ BGE-M3 (Chen và cộng sự, 2024) là các thành phần nền tảng mà dự án kế thừa cho RQ1.
  - Về dữ liệu, bộ VLQA (Nguyen và cộng sự, 2025) gồm 3.129 bộ (câu hỏi, điều luật liên quan, câu trả lời) do chuyên gia gán nhãn trên 59.636 điều luật thuộc 27 lĩnh vực; câu hỏi được thu thập từ các nền tảng tư vấn pháp luật công khai nên phản ánh nhu cầu thực tế của người dân; bộ này cũng là dữ liệu của nhiệm vụ DRiLL tại VLSP 2025. Tuy nhiên, tại thời điểm thực hiện dự án, dữ liệu VLQA chưa được công bố. Cuộc thi Zalo AI Challenge 2021 (Legal Text Retrieval) cung cấp khoảng 3.200 câu hỏi do người viết kèm điều luật liên quan (công bố lại theo giấy phép MIT); dự án chọn lọc các câu thuộc phạm vi kho dữ liệu làm nguồn câu hỏi chính cho thực nghiệm truy xuất.
- **RAG và Agentic-RAG:**
  - Corrective RAG (Yan và cộng sự, 2024) bổ sung bộ đánh giá chất lượng tài liệu truy xuất và kích hoạt hành động khắc phục khi bằng chứng không đủ tin cậy; Self-RAG (Asai và cộng sự, 2024) cho phép mô hình tự quyết định khi nào cần truy xuất và tự phê bình đầu ra. Hai công trình này là cơ sở cho bước đánh giá bằng chứng, viết lại truy vấn và tự kiểm chứng của tác tử trong dự án; khác với Self-RAG, dự án không huấn luyện lại mô hình mà hiện thực các bước này bằng prompt trên đồ thị trạng thái.
  - Với pháp luật Việt Nam, Pham và cộng sự (2025) xây dựng chatbot tư vấn pháp luật dựa trên Agentic-RAG với một Router Agent điều phối các tác tử chuyên biệt và nhiều công cụ (vector search, graph database, web search) trên 54.000 văn bản; trên 1.247 câu hỏi thực tế, hệ thống đạt độ chính xác 82,3%, context precision và context recall cao hơn baseline lần lượt 17,2% và 29,7%. Đây là công trình gần nhất với định hướng của dự án.
- **Đặc trưng của dữ liệu pháp luật:**
  - Reuter và cộng sự (2025) chỉ ra rằng kho văn bản pháp luật chứa nhiều tài liệu có cấu trúc tương tự nhau, khiến hệ thống dễ truy xuất đoạn văn từ sai văn bản nguồn (Document-Level Retrieval Mismatch - DRM), và đề xuất Summary-Augmented Chunking bổ sung ngữ cảnh cấp văn bản cho từng đoạn để giảm DRM. Dự án áp dụng ý tưởng này ở dạng gọn hơn: gắn tiêu đề phân cấp (tên văn bản, Điều, tên Điều) vào từng đoạn, và dùng tỷ lệ DRM làm chỉ số cho RQ2.
  - LegalBench-RAG (Pipitone & Houir Alami, 2024) nhấn mạnh việc đánh giá riêng bước truy xuất trong RAG pháp luật, yêu cầu truy xuất chính xác đoạn văn bản tối thiểu làm căn cứ thay vì cả văn bản; dự án theo hướng này khi chọn Khoản làm đơn vị truy xuất và đánh giá truy xuất độc lập với bước sinh.
- **Trích dẫn và đánh giá:**
  - ALCE (Gao và cộng sự, 2023) đề xuất khung đánh giá khả năng sinh văn bản kèm trích dẫn của LLM với các chỉ số citation recall và citation precision, cho thấy ngay cả các mô hình mạnh vẫn thường trích dẫn không hỗ trợ cho khẳng định. RAGAS (Es và cộng sự, 2024) đề xuất chấm hệ thống RAG bằng LLM mà không cần nhãn chuẩn, trong đó có chỉ số Faithfulness; chỉ số Answer Correctness (so với đáp án mẫu) có trong thư viện ragas đi kèm. Dự án dùng định nghĩa của hai khung này, điều chỉnh để phù hợp giới hạn API miễn phí.

**Khoảng trống nghiên cứu:** Theo khảo sát của nhóm, các hệ thống hỏi đáp pháp luật tiếng Việt nêu trên coi kho văn bản là tĩnh và chỉ gồm văn bản hiện hành, trong khi nhiều câu hỏi thực tế liên quan đến tình huống xảy ra trong quá khứ, khi một văn bản khác đang có hiệu lực. Bên cạnh đó, các hệ thống Agentic-RAG thường được đánh giá tổng thể, ít tách riêng đóng góp của từng thành phần (định tuyến, viết lại truy vấn, kiểm chứng trích dẫn) và chi phí tương ứng. Dự án hướng đến lấp khoảng trống này bằng: (1) truy xuất có xét đến khoảng hiệu lực tại thời điểm của tình huống; (2) tác tử có bước kiểm chứng trích dẫn; (3) đánh giá bằng nghiên cứu lược bỏ trên dữ liệu pháp luật Việt Nam.

## 8. Phạm vi/ giới hạn nghiên cứu

- **Phạm vi nghiên cứu (Scope of Project):**
- **Dữ liệu (Data Scope):**
  - Tập trung vào văn bản luật thành văn thuộc 4 lĩnh vực phổ biến, gồm 5 văn bản: Bộ luật Dân sự (2015), Bộ luật Lao động (2019), Luật Doanh nghiệp (2020) và Luật Thương mại (2005) ở dạng văn bản gốc khi ban hành; cùng Bộ luật Lao động (2012) đã hết hiệu lực, chỉ dùng cho thực nghiệm hiệu lực theo thời gian (RQ4).
  - Dữ liệu được chuẩn hóa và trích xuất đầy đủ các trường thông tin: Số hiệu văn bản, Cơ quan ban hành, Ngày ban hành, Ngày có hiệu lực, Ngày hết hiệu lực, Trạng thái hiệu lực và Cây cấu trúc phân cấp (Văn bản → Chương → Mục → Điều → Khoản → Điểm).
  - Đơn vị truy xuất là Khoản; hệ thống đồng thời cho phép truy xuất toàn văn Điều chứa Khoản đó.
- **Nhiệm vụ (Task Scope):**
  - Tiếp nhận câu hỏi tra cứu pháp luật tự nhiên bằng tiếng Việt từ người dùng.
  - Định tuyến câu hỏi, truy xuất chính xác các đoạn văn bản pháp lý (Điều/Khoản) làm căn cứ trả lời, và từ chối trả lời khi câu hỏi ngoài phạm vi hoặc không đủ căn cứ.
  - Sinh câu trả lời giải thích tự nhiên, súc tích và tự động gắn thẻ trích dẫn (citations) tương ứng với từng khẳng định.
- **Xử lý (Processing Scope):**
  - Tiền xử lý và làm sạch văn bản luật: loại bỏ ký tự rác, chuẩn hóa định dạng văn bản tiếng Việt.
  - Áp dụng kỹ thuật phân đoạn đệ quy theo cấu trúc văn bản pháp luật (Recursive Legal Chunking) để không làm đứt đoạn quy phạm.
  - Tạo chỉ mục kép (Dual Indexing): Sparse Index (BM25) và Dense Index (Vector Database ChromaDB với mô hình embedding đa ngôn ngữ BGE-M3).
- **Trích dẫn (Citation Scope):**
  - Trích dẫn bắt buộc phải trỏ đến đơn vị quy phạm cụ thể (tối thiểu là cấp Điều, ưu tiên cấp Khoản khi có căn cứ rõ ràng).
  - Cho phép người dùng đối chiếu chéo trực tiếp nội dung trích dẫn với nguyên văn điều luật gốc trên giao diện.
- **Đánh giá (Evaluation Scope):**
  - Xây dựng bộ dữ liệu kiểm thử (Evaluation Dataset) khoảng 170–180 câu hỏi kèm nhãn căn cứ chuẩn, phân loại theo: tình huống, có mốc thời gian, tra cứu trực tiếp, ngoài phạm vi; mỗi câu ghi rõ nguồn (zalo / synthetic / manual) và kết quả được báo cáo tách theo nguồn. Câu tổng hợp được kiểm định bằng đối chiếu tay một mẫu 20 câu; câu tự soạn được thành viên còn lại kiểm tra chéo căn cứ. Câu từ Zalo chỉ có nhãn cấp Điều nên chỉ được dùng cho các chỉ số cấp Điều.
- **Đánh giá định lượng qua các chỉ số:**
  - Khâu truy xuất (tính tự động theo nhãn chuẩn): Hit Rate@5, Recall@10, MRR@10, tỷ lệ DRM. Thực nghiệm so sánh phương pháp phân đoạn được đánh giá ở cấp Điều để đảm bảo công bằng giữa các phương pháp.
  - Khâu trích dẫn và hiệu lực (tính tự động theo nhãn chuẩn): Citation Precision, Citation Recall, tỷ lệ trích dẫn đúng phiên bản văn bản, tỷ lệ từ chối đúng câu hỏi ngoài phạm vi.
  - Khâu sinh câu trả lời (LLM-as-a-judge, dùng nhà cung cấp LLM khác với tác tử): Faithfulness, Answer Correctness; độ tin cậy của bộ chấm được kiểm định bằng đối chiếu với chấm tay của nhóm trên 20 câu trả lời.
  - Chi phí: độ trễ (đo ở lần chạy không dùng cache) và số lượt gọi LLM trên mỗi câu hỏi.
- **Kỹ thuật (Technical & Architectural Scope):**
  - Backend: Python, LangGraph (tác tử), FastAPI.
  - Mô hình ngôn ngữ (LLM): Sử dụng API miễn phí (Gemini Flash hoặc mô hình nguồn mở như Llama / Qwen qua Groq) thông qua giao diện tương thích OpenAI, cho phép thay đổi nhà cung cấp bằng cấu hình; kết quả gọi LLM được lưu đệm (cache) để giảm số lượt gọi khi chạy thực nghiệm.
  - Embedding và Reranker chạy cục bộ: BGE-M3 và bge-reranker-v2-m3.
  - Cơ sở dữ liệu: ChromaDB (lưu trữ vector và metadata); lịch sử hội thoại chỉ lưu trong phiên làm việc.
- **Ứng dụng (Application Scope):**
  - Xây dựng bản thử nghiệm tương tác hoàn chỉnh (Interactive Prototype) dạng Web Application (Streamlit + FastAPI).
  - Giao diện hiển thị trực quan: Hộp chat hỏi đáp, khung hiển thị câu trả lời có đánh dấu chỉ mục trích dẫn, và panel bên cạnh cho phép đọc toàn văn điều luật gốc khi người dùng nhấp vào trích dẫn.
- **Giới hạn nghiên cứu (Project Limitations):**
  - Giới hạn về nguồn văn bản: Hệ thống chỉ giới hạn trong kho dữ liệu đã thu thập và chuẩn hóa thuộc 4 lĩnh vực nêu trên; không bao gồm Nghị định, Thông tư hướng dẫn thi hành; chưa hỗ trợ tự động thu thập (crawl) và cập nhật văn bản theo thời gian thực từ Cổng thông tin Chính phủ.
  - Giới hạn về quan hệ giữa văn bản: Hệ thống chưa khai thác tự động quan hệ dẫn chiếu, sửa đổi, bổ sung giữa các văn bản; hiệu lực được xử lý ở cấp văn bản (khoảng hiệu lực), chưa xử lý ở cấp từng Điều/Khoản bị sửa đổi.
  - Giới hạn về phiên bản văn bản: Kho dữ liệu dùng văn bản gốc khi ban hành, chưa hợp nhất các lần sửa đổi, bổ sung sau đó (ví dụ các luật sửa đổi Luật Doanh nghiệp 2020); câu trả lời có thể không phản ánh nội dung đã được sửa đổi.
  - Giới hạn về loại hình dữ liệu: Tập trung duy nhất vào văn bản quy phạm pháp luật thành văn (Statutory Law); không bao gồm án lệ, bản án tòa án hay các tình huống tranh tụng thực tế.
  - Giới hạn về tư vấn pháp lý: Hệ thống chỉ đóng vai trò công cụ hỗ trợ tra cứu và cung cấp thông tin tham khảo, không có giá trị pháp lý chính thức và không thay thế cho ý kiến tư vấn của luật sư.
  - Giới hạn về tài nguyên tính toán và thời gian: Dự án tập trung vào kỹ thuật đóng gói hệ thống phần mềm (Engineering & System Integration) trước hạn chót 04/12/2026; không thực hiện tiền huấn luyện (pre-train) hay fine-tune mô hình nền tảng từ đầu.

## 9. Nội dung/ phương pháp nghiên cứu

### 9.1. Nội dung nghiên cứu chính (Kỹ thuật và Phát triển hệ thống)

- **Nội dung 1: Thu thập, tiền xử lý và cấu trúc hóa cơ sở dữ liệu pháp luật:**
  - Thu thập toàn văn văn bản luật thuộc phạm vi: Bộ luật Dân sự (2015), Bộ luật Lao động (2019), Luật Doanh nghiệp (2020), Luật Thương mại (2005) ở dạng văn bản gốc, và Bộ luật Lao động (2012) đã hết hiệu lực. Quy trình: file .doc gốc → chuyển sang Markdown (MinerU) → bóc tách cây cấu trúc thành JSON → phân đoạn.
  - Làm sạch văn bản, bóc tách cấu trúc phân cấp và trích xuất siêu dữ liệu (Số hiệu văn bản, Cơ quan ban hành, Ngày ban hành, Ngày có hiệu lực, Ngày hết hiệu lực, Trạng thái hiệu lực).
  - Cài đặt thuật toán phân đoạn đệ quy theo cấu trúc văn bản luật (Recursive Legal Chunking) để chia nhỏ dữ liệu theo các cấp Chương → Mục → Điều → Khoản (Điểm được giữ trong Khoản) mà không làm gãy ranh giới ngữ nghĩa.
- **Nội dung 2: Xây dựng và đánh giá Pipeline Truy xuất Đa phương pháp (Retrieval Pipeline):**
  - Xây dựng chỉ mục thưa (Sparse Index) sử dụng giải thuật BM25 nhằm bắt chính xác số hiệu văn bản và thuật ngữ pháp lý.
  - Xây dựng chỉ mục vector (Dense Index) trên Vector Database ChromaDB sử dụng mô hình embedding hỗ trợ tốt tiếng Việt (BGE-M3).
  - Cài đặt cơ chế tìm kiếm lai (Hybrid Search) kết hợp lọc siêu dữ liệu theo khoảng hiệu lực (Metadata Filtering) và mô hình xếp hạng lại (Cross-Encoder Reranker) để tối ưu độ chính xác của các đoạn căn cứ trả về.
- **Nội dung 3: Phát triển Tác tử Agentic-RAG và Cơ chế Kiểm chứng Trích dẫn:**
  - Xây dựng tác tử bằng LangGraph với các nút: định tuyến (route), tra cứu trực tiếp điều luật (lookup_article), truy xuất có lọc hiệu lực theo thời điểm (retrieve), đánh giá bằng chứng và viết lại truy vấn (grade), sinh câu trả lời (generate), kiểm chứng trích dẫn (verify).
  - Xây dựng prompt ràng buộc yêu cầu mô hình gắn mã trích dẫn cho từng khẳng định, trỏ chính xác đến Điều/Khoản làm căn cứ; xây dựng bộ phân giải và kiểm chứng trích dẫn.
  - Cài đặt baseline RAG một lượt và các cờ cấu hình bật/tắt từng thành phần của tác tử để phục vụ thực nghiệm so sánh và lược bỏ (ablation).
  - Ghi lại vết thực thi (trace) các bước tác tử đã thực hiện để hiển thị trên giao diện và phục vụ phân tích lỗi.
- **Nội dung 4: Xây dựng Giao diện Người dùng và Tích hợp Hệ thống (Web Prototype):**
  - Xây dựng ứng dụng web tương tác hoàn chỉnh (Streamlit + FastAPI).
  - Tích hợp các tính năng: giao diện chat tự nhiên, hiển thị câu trả lời có đánh dấu số trích dẫn, bảng phụ (Side Panel) cho phép nhấp vào trích dẫn để đọc trực tiếp nguyên văn điều luật tương ứng, khung hiển thị vết thực thi của tác tử (định tuyến, truy vấn đã viết lại, trích dẫn bị loại khi kiểm chứng).
- **Nội dung 5: Đánh giá Thực nghiệm và Tối ưu hóa:**
  - Xây dựng bộ dữ liệu kiểm thử (Evaluation Dataset) khoảng 170–180 câu hỏi có gán nhãn căn cứ chuẩn từ ba nguồn (Zalo AI 2021, câu tổng hợp, câu tự soạn), phân loại theo tình huống / mốc thời gian / tra cứu trực tiếp / ngoài phạm vi.
  - Chạy các thực nghiệm RQ1–RQ4: so sánh phương pháp truy xuất, phương pháp phân đoạn, RAG một lượt với Agentic-RAG và các cấu hình lược bỏ, các chế độ lọc hiệu lực.
  - Đo lường định lượng theo các chỉ số tại mục 8 (Phạm vi đánh giá), xuất kết quả dạng CSV cho từng cấu hình và bảng tổng hợp cho từng câu hỏi nghiên cứu.
  - Phân tích lỗi (Error Analysis) trên các câu trả lời sai và tinh chỉnh tham số (top-k, rerank-k, prompt template).

### 9.2. Phương pháp nghiên cứu

- **Phương pháp Kỹ thuật Phần mềm (Software Engineering Methodology):**
  - Áp dụng mô hình phát triển phần mềm linh hoạt (Agile/Scrum rút gọn), chia dự án thành các chu kỳ chạy nước rút (sprints 1–2 tuần) để liên tục tích hợp, kiểm thử và bàn giao sản phẩm trước hạn chót 04/12/2026.
- **Phương pháp Tổ chức và Lưu trữ Dữ liệu Phân cấp (Hierarchical Chunking):**
  - Tổ chức dữ liệu theo định dạng JSON/JSONL có cấu trúc, lưu trữ metadata phong phú kèm theo từng đoạn chunk để phục vụ việc lọc theo khoảng hiệu lực tại thời điểm của tình huống trước khi truy xuất.
- **Phương pháp Truy xuất Thông tin Kết hợp (Hybrid Information Retrieval):**
  - Kết hợp điểm số BM25 và Vector Cosine Similarity theo kỹ thuật Reciprocal Rank Fusion (RRF), sau đó đưa qua Cross-Encoder Reranker để chọn lọc top-k đoạn ngữ cảnh phù hợp nhất.
- **Phương pháp Đánh giá Hệ thống RAG (RAG Evaluation Framework):**
  - Các chỉ số truy xuất, trích dẫn và hiệu lực được tính tự động bằng đối chiếu với nhãn chuẩn. Faithfulness và Answer Correctness được chấm bằng LLM-as-a-judge theo định nghĩa của Ragas, với prompt chấm gọn (một lượt gọi mỗi câu trả lời) để phù hợp giới hạn API miễn phí; bộ chấm được kiểm định bằng mức đồng thuận với chấm tay của nhóm.
  - Phương pháp nghiên cứu lược bỏ (Ablation Study): bật/tắt từng thành phần của tác tử để đo đóng góp riêng của từng thành phần.

## 10. Dự kiến kết quả/ Đề suất giải pháp

### 10.1. Đề xuất Giải pháp và Kiến trúc Hệ thống (Proposed Architecture)

Kiến trúc hệ thống hỏi đáp pháp luật tiếng Việt gồm 4 phân hệ chính:

1. **Phân hệ ETL & Quản trị Dữ liệu (Data Pipeline):**
  - Module tiền xử lý, phân đoạn đệ quy theo cấu trúc điều khoản và trích xuất metadata.
  - Kho lưu trữ kép: Vector Database (ChromaDB) phục vụ Dense Search và Inverted Index phục vụ BM25 Search.
2. **Động cơ Truy xuất Căn cứ Pháp lý (Retrieval Engine) — các công cụ của tác tử:**
  - search(query, k, date): tìm kiếm lai BM25 + Dense (RRF) kết hợp Cross-Encoder Reranker, lọc văn bản theo khoảng hiệu lực tại thời điểm date.
  - get_article(law_id, article): truy xuất toàn văn một Điều.
3. **Tác tử Agentic-RAG (LangGraph Agent):**
  - Định tuyến câu hỏi và trích xuất thời điểm của tình huống; vòng đánh giá bằng chứng và viết lại truy vấn; sinh câu trả lời có trích dẫn.
  - Bộ kiểm chứng trích dẫn (Citation Verifier): đối chiếu mã trích dẫn với ngữ cảnh và kiểm tra mức độ hỗ trợ của đoạn luật đối với từng khẳng định.
4. **Phân hệ Giao diện Người dùng (Interactive User Interface):**
  - Giao diện Web tương tác hiển thị khung chat, bảng tra cứu văn bản gốc và vết thực thi của tác tử.

### 10.2. Dự kiến Kết quả Đạt được (Expected Deliverables)

- **Kho Dữ liệu Pháp luật Có cấu trúc:**
  - Bộ cơ sở dữ liệu làm sạch và chuẩn hóa gồm 5 văn bản thuộc 4 lĩnh vực luật chính, được phân đoạn hoàn chỉnh theo cấu trúc phân cấp và gán nhãn khoảng thời gian hiệu lực.
- **Mã nguồn Hệ thống Hoàn chỉnh (Full-Stack Source Code):**
  - Toàn bộ mã nguồn Python cài đặt pipeline dữ liệu, hybrid retrieval, agent sinh câu trả lời và backend/frontend.
  - Đóng gói mã nguồn sạch (Clean Code, tài liệu hướng dẫn cài đặt README.md, file cấu hình môi trường requirements.txt / Dockerfile).
- **Bản thử nghiệm Ứng dụng Hoàn chỉnh (Interactive Web Prototype):**
  - Ứng dụng Web hoạt động ổn định, cho phép người dùng hỏi đáp theo thời gian thực và xem căn cứ trích dẫn trực tiếp.
- **Bộ Dữ liệu Kiểm thử và Bảng Kết quả Thực nghiệm:**
  - Tập kiểm thử khoảng 170–180 câu hỏi pháp luật kèm nhãn chuẩn, phân loại theo 4 loại câu hỏi và 3 nguồn.
  - Bảng số liệu trả lời từng câu hỏi nghiên cứu: so sánh chiến lược truy xuất (RQ1), phương pháp phân đoạn (RQ2), RAG một lượt vs. Agentic-RAG và ablation (RQ3), các chế độ lọc hiệu lực (RQ4).
- **Báo cáo Tổng kết Dự án Công nghệ Thông tin:**
  - Cuốn báo cáo hoàn chỉnh trình bày kiến trúc kỹ thuật, quy trình thực hiện dự án (SDLC), phân công nhiệm vụ, kết quả thực nghiệm và hướng phát triển.

---

## 11. Kế hoạch thực hiện tiến độ dự kiến

- Thời gian thực hiện: Từ 15/08/2026 đến 04/12/2026 (khoảng 16 tuần). Giai đoạn triển khai kỹ thuật gồm 6 sprint từ 09/10/2026; phân công chi tiết từng nhiệm vụ xem Phụ lục B.
- Phân công vai trò: Phạm Huỳnh Quốc Đạt phụ trách lõi kỹ thuật (truy xuất, tác tử, API, đánh giá tự động); Hoàng Sinh Hùng phụ trách dữ liệu (kho văn bản, tập kiểm thử), giao diện và báo cáo.

### Giai đoạn 0 (15/08 – 08/10/2026): Khảo sát và đề cương

- Nội dung: Khảo sát tài liệu, lựa chọn đề tài, xác định phạm vi và kiến trúc, hoàn thiện đề cương.
- Phụ trách: Cả 2 thành viên.
- Kết quả: Đề cương hoàn chỉnh; khung mã nguồn (repository) được khởi tạo.
- Tiến độ tích lũy: 15%.

### Sprint 1 (09/10 – 14/10/2026): Dữ liệu và nền tảng

- Nội dung: Thu thập và làm sạch 5 văn bản; phân đoạn theo cấu trúc và nạp vector database; client LLM có cache; bắt đầu tập kiểm thử.
- Kết quả: Kho dữ liệu 5 văn bản đã phân đoạn kèm khoảng hiệu lực; chỉ mục ChromaDB; 30 câu kiểm thử đầu tiên.
- Tiến độ tích lũy: 25%.

### Sprint 2 (15/10 – 21/10/2026): Truy xuất và thực nghiệm RQ1, RQ2

- Nội dung: BM25, Dense, Hybrid (RRF), Reranker, lọc hiệu lực theo thời điểm; các biến thể phân đoạn; đánh giá truy xuất tự động; nhập câu hỏi Zalo và câu tổng hợp, soạn câu tự soạn; khung giao diện.
- Kết quả: Bảng số liệu RQ1 và RQ2; tập kiểm thử đã kiểm tra hợp lệ (python -m eval.import_cases).
- Tiến độ tích lũy: 40%.

### Sprint 3 (22/10 – 28/10/2026): Tác tử Agentic-RAG

- Nội dung: Đồ thị LangGraph với 6 nút, baseline RAG một lượt, cờ ablation, vết thực thi; giao diện chat và panel trích dẫn.
- Kết quả: Tác tử trả lời được qua dòng lệnh với đủ các nhánh; giao diện chạy với dữ liệu mẫu.
- Tiến độ tích lũy: 60%.

### Sprint 4 (29/10 – 04/11/2026): Tích hợp hệ thống và đánh giá câu trả lời

- Nội dung: API FastAPI; ghép giao diện với backend; đánh giá câu trả lời bằng LLM-as-a-judge; kiểm định bộ chấm bằng chấm tay.
- Kết quả: Bản thử nghiệm chạy hoàn chỉnh từ đầu đến cuối (End-to-End MVP); pipeline đánh giá chạy được.
- Tiến độ tích lũy: 75%.

### Sprint 5 (05/11 – 15/11/2026): Thực nghiệm đầy đủ và viết báo cáo

- Nội dung: Chạy thực nghiệm RQ3, RQ4; phân tích lỗi; viết các chương báo cáo. Đóng băng tính năng ngày 12/11.
- Kết quả: Đầy đủ bảng số liệu và biểu đồ RQ1–RQ4; bản nháp báo cáo khoảng 80%.
- Tiến độ tích lũy: 90%.

### Sprint 6 (16/11 – 27/11/2026): Đóng gói và hoàn thiện

- Nội dung: Docker, README, dọn mã nguồn; hoàn thiện báo cáo theo mẫu TDTU; slide và video demo.
- Kết quả: Báo cáo hoàn chỉnh ngày 27/11; rà soát và dự phòng 28/11–03/12; nộp ngày 03/12, hạn chót 23:59 ngày 04/12/2026.
- Tiến độ tích lũy: 100%.

**Phương án dự phòng:**

- Bộ VLQA chưa được công bố dữ liệu (kiểm tra ngày 15/10/2026): đã chuyển sang Zalo AI Legal Text Retrieval 2021 kết hợp câu tổng hợp và câu tự soạn.
- Nếu đến 28/10 tác tử chưa hoạt động ổn định: lược bỏ nút đánh giá bằng chứng và vòng viết lại truy vấn, giữ định tuyến và kiểm chứng trích dẫn; RQ3 thực hiện ablation trên 2 thành phần.
- Nếu quota API miễn phí không đủ: chạy cấu hình baseline và full trên toàn bộ tập kiểm thử, các cấu hình ablation trên tập con khoảng 80 câu cân bằng theo nguồn và lĩnh vực.

## 12. Tài liệu tham khảo

- Asai, A., Wu, Z., Wang, Y., Sil, A., & Hajishirzi, H. (2024). Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection. The Twelfth International Conference on Learning Representations (ICLR 2024).
- Chen, J., Xiao, S., Zhang, P., Luo, K., Lian, D., & Liu, Z. (2024). M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation. Findings of the Association for Computational Linguistics: ACL 2024, 2318–2335. https://doi.org/10.18653/v1/2024.findings-acl.137
- Cormack, G. V., Clarke, C. L. A., & Büttcher, S. (2009). Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods. Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval, 758–759. https://doi.org/10.1145/1571941.1572114
- Do, D.-T., Luu, S. T., Pham, T., Vo, T., Chu, N.-H., Chu, Q.-H., Hoang, C. D., Nguyen, T.-M., Trieu, A., Nguyen, D., Nguyen, H., Nguyen, T.-H., Le, N.-K., Nguyen, D.-H., Le, N.-C., Le, T.-T., Dang, H.-A., Nguyen, H.-T., Tran, V., & Nguyen, L.-M. (2025). A Summary of the ALQAC 2025 Competition. 2025 17th International Conference on Knowledge and System Engineering (KSE), 1–6. https://doi.org/10.1109/KSE68178.2025.11309650
- Es, S., James, J., Espinosa Anke, L., & Schockaert, S. (2024). RAGAS: Automated Evaluation of Retrieval Augmented Generation. Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations (EACL 2024), 150–158. https://doi.org/10.18653/v1/2024.eacl-demo.16
- Gao, T., Yen, H., Yu, J., & Chen, D. (2023). Enabling Large Language Models to Generate Text with Citations. Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP 2023), 6465–6488. https://doi.org/10.18653/v1/2023.emnlp-main.398
- Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. Advances in Neural Information Processing Systems 33 (NeurIPS 2020), 9459–9474.
- Nguyen Ba, T., Doan The, V., Pham Quang, T., & Tran Van, T. (2024). Vietnamese Legal Information Retrieval in Question-Answering System. arXiv preprint arXiv:2409.13699.
- Nguyen, T.-M., Nguyen, H.-T., Dao, T.-K., Phan, X.-H., Nguyen, H.-T., & Vuong, T.-H.-Y. (2025). VLQA: The First Comprehensive, Large, and High-Quality Vietnamese Dataset for Legal Question Answering. arXiv preprint arXiv:2507.19995.
- Pham, H., Duong, N. T. N., & Pham, T. N. H. (2025). Agentic RAG-Based Legal Advisory Chatbot: A Knowledge-Driven Approach for Vietnamese Legal System. Proceedings of the 17th International Joint Conference on Knowledge Discovery, Knowledge Engineering and Knowledge Management (IC3K 2025) - Volume 2: KMIS, 257–266. SciTePress. https://doi.org/10.5220/0013735400004000
- Pipitone, N., & Houir Alami, G. (2024). LegalBench-RAG: A Benchmark for Retrieval-Augmented Generation in the Legal Domain. arXiv preprint arXiv:2408.10343.
- Reuter, M., Lingenberg, T., Liepina, R., Lagioia, F., Lippi, M., Sartor, G., Passerini, A., & Sayin, B. (2025). Towards Reliable Retrieval in RAG Systems for Large Legal Datasets. Proceedings of the Natural Legal Language Processing Workshop 2025 (NLLP 2025), 17–30. https://doi.org/10.18653/v1/2025.nllp-1.3
- Robertson, S., & Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond. Foundations and Trends in Information Retrieval, 3(4), 333–389. https://doi.org/10.1561/1500000019
- Yan, S.-Q., Gu, J.-C., Zhu, Y., & Ling, Z.-H. (2024). Corrective Retrieval Augmented Generation. arXiv preprint arXiv:2401.15884.
- Zalo AI. (2021). Zalo AI Challenge 2021 – Legal Text Retrieval. https://challenge.zalo.ai/

## PHỤ LỤC A. QUY ƯỚC DỮ LIỆU CHUNG (thống nhất trước ngày 10/10/2026)

### A.1. Quy trình và file văn bản (cập nhật 15/10/2026)

- Mã văn bản (LAW_ID): BLDS2015, BLLD2019, BLLD2012, LDN2020, LTM2005.
- data/raw/<số hiệu>_<tên>.doc (file gốc) → data/normalized/<...>.md (MinerU) → data/structured/<...>.json (data/legal_structure_parser.py). File JSON cấu trúc là đầu vào chuẩn cho bộ phân đoạn src/ingestion/legal_chunker.py.
- JSON cấu trúc: law {law_number, name, parts[], chapters[], articles[]} → part {chapters[], articles[]} → chapter {number, title, sections[], articles[]} → section {number, title, articles[]} → article {number, title, text, clauses[]} → clause {number, text, points[]} → point {number, text}.
- law_number trong JSON phải trùng trường "number" của văn bản đó trong laws.json.

### A.2. Siêu dữ liệu văn bản: data/raw/laws.json

```json
{
  "BLLD2012": {
    "document": "Bộ luật Lao động 2012",
    "number": "10/2012/QH13",
    "issued_date": "2012-06-18",
    "effective_date": "2013-05-01",
    "expiry_date": "2021-01-01",
    "status": "Hết hiệu lực",
    "domain": "lao_dong",
    "source": "<đường dẫn nguồn đã lấy văn bản>"
  }
}
```

- expiry_date = null nếu văn bản còn hiệu lực. Văn bản có hiệu lực tại ngày d khi effective_date ≤ d < expiry_date.

### A.3. Đoạn văn bản (chunk): data/processed/chunks.jsonl, mỗi dòng một đối tượng

```json
{
  "chunk_id": "BLDS2015_Dieu357_Khoan1",
  "law_id": "BLDS2015",
  "document": "Bộ luật Dân sự 2015",
  "chapter": "Chương XVIII",
  "section": "Mục 2",
  "article": "Điều 357",
  "article_title": "Trách nhiệm do chậm thực hiện nghĩa vụ trả tiền",
  "clause": "Khoản 1",
  "point": null,
  "content": "Trường hợp bên có nghĩa vụ chậm trả tiền thì ...",
  "effective_date": "2017-01-01",
  "expiry_date": null,
  "status": "Còn hiệu lực"
}
```

- chunk_id = <LAW_ID>_Dieu<số>[_Khoan<số>]. Điều không có khoản dùng <LAW_ID>_Dieu<số>; phần dẫn nhập của Điều có khoản cũng dùng <LAW_ID>_Dieu<số>.
- Khóa Điều (article key) của một chunk = chunk_id bỏ phần _Khoan<số>, ví dụ BLDS2015_Dieu357.
- Ba file: chunks.jsonl (theo Khoản), chunks_article.jsonl (theo Điều, chunk_id = khóa Điều), chunks_fixed.jsonl (cố định theo số từ, chunk_id = <LAW_ID>_fixed<n>, thêm trường articles là danh sách "Điều N" mà đoạn phủ qua).

### A.4. Câu hỏi kiểm thử: eval/test_cases.json (danh sách đối tượng)

```json
{
  "id": "Q001",
  "question": "Năm 2020 tôi ký hợp đồng lao động theo mùa vụ 6 tháng, hợp đồng này có hợp lệ không?",
  "type": "temporal",
  "domain": "lao_dong",
  "event_date": "2020-03-01",
  "gold_citations": ["BLLD2012_Dieu22_Khoan1"],
  "reference_answer": "...",
  "source": "manual",
  "checked_by": "Dat"
}
```

- type ∈ {situational, temporal, direct, out_of_scope}; domain ∈ {dan_su, lao_dong, doanh_nghiep, thuong_mai, ngoai_pham_vi}.
- event_date chỉ bắt buộc với câu temporal; câu out_of_scope có gold_citations rỗng.
- source ∈ {zalo, synthetic, manual}. gold_citations là chunk_id cấp Khoản hoặc khóa Điều (khi chỉ biết căn cứ ở cấp Điều, như câu từ Zalo); liệt kê đủ mọi căn cứ cần thiết.
- reference_answer có thể để trống với câu Zalo cho đến Sprint 3; checked_by = null nếu chưa ai kiểm tra.

### A.5. Kết quả API: POST /api/ask

**Yêu cầu:** { "question": "...", "config": "full" }

**Phản hồi:**

```json
{
  "answer": "... [BLDS2015_Dieu357_Khoan1] ...",
  "refused": false,
  "citations": [ { "chunk_id": "...", "document": "...", "article": "...", "clause": "...", "content": "..." } ],
  "retrieved_chunks": [ { "chunk_id": "...", "score": 0.83 } ],
  "trace": [ { "node": "route", "output": { "type": "situational", "event_date": null }, "ms": 820, "llm_calls": 1 } ]
}
```

- config ∈ {baseline, full, no_router, no_grading, no_verify}.

## PHỤ LỤC B. PHÂN CÔNG CHI TIẾT THEO SPRINT

(Ký hiệu: [x] đã hoàn thành; [ ] chưa làm; "Xong khi" là tiêu chí nghiệm thu của nhiệm vụ.)

### SPRINT 1 (09/10 – 14/10/2026): DỮ LIỆU VÀ NỀN TẢNG

**Mục tiêu sprint:** kho dữ liệu 5 văn bản đã phân đoạn và nạp ChromaDB; client LLM sẵn sàng; 30 câu kiểm thử đầu tiên.

**Phạm Huỳnh Quốc Đạt:**

- [x] Khởi tạo repository, cấu trúc thư mục, requirements.txt (cố định phiên bản), README hướng dẫn cài đặt.
- [x] legal_chunker.py: tách Chương → Mục → Điều → Khoản, giữ Điểm trong Khoản; hàm fixed_chunk cho baseline RQ2; kiểm thử tự động.
- [x] index.py: nạp chunk vào ChromaDB kèm metadata, văn bản embed có gắn tiêu đề phân cấp; cờ --rebuild, --query; kiểm thử tự động.
- [x] Bổ sung trường expiry_date từ laws.json vào từng chunk. Xong khi: kiểm thử chunk của BLLD2012 có expiry_date = "2021-01-01".
- [x] fixed_chunk ghi danh sách các Điều mà mỗi đoạn cố định phủ qua (trường "articles") để đánh giá RQ2 ở cấp Điều. Xong khi: kiểm thử một đoạn nằm vắt qua hai Điều trả về đủ cả hai.
- [x] Chạy chunker trên 5 file của Hùng; đối chiếu số Điều với mục lục văn bản (BLDS2015: 689, BLLD2019: 220, BLLD2012: 242, LDN2020: 218, LTM2005: 324, cộng các điều bổ sung trong bản hợp nhất). Xong khi: số Điều khớp, không có chunk rỗng. → chuyển sang Sprint 2 (Task 1, 8).
- [x] Sửa bộ tách cho các trường hợp phát sinh từ dữ liệu thật (điều bị bãi bỏ, điều có số kèm chữ như 50a, dòng chú thích sửa đổi còn sót). → chuyển sang Sprint 2 (Task 1, 8).
- [x] Chạy index.py với BGE-M3 trên dữ liệu thật. Xong khi: truy vấn "lãi chậm trả tiền" trả về BLDS2015 Điều 357 trong top-5. → chuyển sang Sprint 2 (Task 1, 8).
- [x] src/generation/llm.py: client tương thích OpenAI (LLM_BASE_URL, LLM_API_KEY, LLM_MODEL đọc từ .env); cache xuống đĩa theo hash (model, messages, tham số); tự chờ và thử lại khi gặp lỗi 429; đếm số lượt gọi; hàm chat_json phân tích JSON, thử lại 1 lần khi lỗi. Xong khi: kiểm thử với client giả chứng minh lần gọi thứ hai lấy từ cache và lỗi 429 được thử lại.
- [x] Cập nhật .env.example (LLM_*, JUDGE_*, EMBED_MODEL); đăng ký API key Gemini và Groq, gọi thử mỗi bên 1 lần. → Gemini (gemini-3.1-flash-lite) gọi thử xong 16/10; Groq chuyển sang Sprint 4.

**Hoàng Sinh Hùng:**

- [x] Tải và chuẩn hóa 4 luật (BLDS 2015, BLLĐ 2019, LDN 2020, LTM 2005) bằng pipeline .doc → MinerU → normalized/*.md → structured/*.json; số Điều khớp mục lục. (Văn bản gốc, chưa hợp nhất sửa đổi — ghi là giới hạn.)
- [x] Định dạng Phụ lục A.1 cũ (data/raw/<LAW_ID>.md) được thay bằng JSON cấu trúc (Phụ lục A.1 cập nhật 15/10).
- [x] Soạn 65 câu kiểm thử đầu tiên (data/test_cases.json, sinh bằng AI → nguồn synthetic).
- [x] BLLĐ 2012, laws.json, kiểm tra chất lượng → chuyển sang Sprint 2 (H1–H3).
- [ ] Xin VLQA: hủy — dữ liệu chưa được công bố (kiểm tra 15/10); thay bằng Zalo AI 2021.
- [ ] eval/README.md: hủy — quy ước gán nhãn nằm trong thẻ H6 của plan Sprint 2.

**Cả hai:** thống nhất Phụ lục A ngày 10/10; họp nhanh 10 phút mỗi tối.

**Nghiệm thu sprint (14/10):** chunks.jsonl đủ 5 văn bản; ChromaDB đã nạp; 30 câu kiểm thử đúng schema.

### SPRINT 2 (15/10 – 21/10/2026): TRUY XUẤT VÀ THỰC NGHIỆM RQ1, RQ2

**Mục tiêu sprint:** kho chunk đọc từ JSON cấu trúc; truy xuất BM25 / Dense / Hybrid / Hybrid + rerank có lọc hiệu lực; tập kiểm thử 3 nguồn (zalo, synthetic, manual) hợp lệ; bảng số liệu RQ1, RQ2.

**Phạm Huỳnh Quốc Đạt (chi tiết: vn-legal-qa/docs/superpowers/plans/2026-10-15-sprint2-dat.md):**

- [x] Task 1 — Bộ phân đoạn đọc data/structured/*.json, sinh chunks.jsonl (Khoản), chunks_article.jsonl (Điều), chunks_fixed.jsonl. Xong khi: BLDS 689, BLLĐ 220, LDN 218, LTM 324 Điều (BLLĐ 2012: 242 khi Hùng xong H1).
- [x] Task 2 — eval/cases.py (kiểm tra hợp lệ), eval/import_cases.py (gộp zalo + synthetic + manual), eval/show_article.py; tải tập con Zalo vào data/external/zalo/; thêm domain vào laws.json. Xong khi: python -m eval.import_cases ghi eval/test_cases.json không lỗi.
- [x] Task 3 — Chỉ mục theo 4 biến thể RQ2 (--variant clause_header / clause_plain / article / fixed).
- [x] Task 4 — Lọc hiệu lực theo ngày (filters.py) và BM25 (underthesea).
- [x] Task 5 — Dense trên Chroma có lọc hiệu lực.
- [x] Task 6 — Retriever: RRF (k=60), rerank bge-reranker-v2-m3 top-20, get_article, load_retriever.
- [x] Task 7 — eval/metrics.py + eval/evaluate.py --rq rq1|rq2: Hit@5, Recall@10, MRR@10 (Điều, Khoản), DRM@5, tách theo nguồn.
- [x] Task 8 — Chạy thật (bỏ qua gọi thử API LLM: chưa có key): nạp 4 chỉ mục, đo rerank (> 3 s/câu thì top-10), chạy RQ1 và RQ2, gọi thử API LLM (việc Sprint 1). Xong khi: có eval/results/retrieval_rq1.md và retrieval_rq2.md.
- [x] Kiểm chéo căn cứ các câu manual của Hùng (đổi checked_by thành "Dat").

**Hoàng Sinh Hùng (chi tiết: vn-legal-qa/docs/sprints/2026-10-15-sprint2-hung.md):**

- [x] H1 — Thêm BLLĐ 2012 (structured JSON, 242 Điều).
- [x] H2 — Hoàn thiện laws.json: đối chiếu 4 luật với nguồn chính thức, thêm BLLD2012, domain, source.
- [x] H3 — docs/data_check.md: đối chiếu 10 Điều ngẫu nhiên mỗi văn bản với bản gốc.
- [x] H4 — Duyệt khoảng 81 câu Zalo, câu loại ghi vào eval/zalo_exclude.txt.
- [x] H5 — docs/synthetic_check.md: kiểm định 20/65 câu synthetic, sửa câu sai.
- [x] H6 — eval/manual_cases.json: ~15 situational (BLLĐ, LTM), 10–15 temporal, ~5 direct, ~5 out_of_scope.
- [x] H7 — Khung Streamlit src/ui/app.py với phản hồi mẫu (Phụ lục A.5).

**Nghiệm thu sprint (21/10):** bảng RQ1 và RQ2 có số liệu thật; python -m eval.import_cases chạy không lỗi với đủ 3 nguồn; giao diện mẫu chạy được.

### SPRINT 3 (22/10 – 28/10/2026): TÁC TỬ AGENTIC-RAG

**Mục tiêu sprint:** tác tử chạy được qua dòng lệnh với đủ các nhánh; giao diện chạy với dữ liệu mẫu.

**Phạm Huỳnh Quốc Đạt (chi tiết: docs/superpowers/plans/2026-10-16-sprint3-dat.md):**

- [x] Task 1 — langgraph 1.2.15; gia cố llm.py: đếm lượt gọi logic (requests), giãn cách LLM_MIN_INTERVAL theo 15 RPM, parse JSON không tham lam, xóa cache JSON hỏng, .env theo gốc repo.
- [x] Task 2 — src/generation/citations.py: tách/gỡ/gắn nhãn [chunk_id] theo câu (verify a, b).
- [x] Task 3 — src/generation/prompts.py: 4 prompt tiếng Việt (route, grade, generate, verify), mỗi prompt ≥ 2 ví dụ, đầu ra JSON.
- [x] Task 4 — src/agent/state.py (trạng thái, 5 cấu hình) và nút route (chuẩn hóa law_id, event_date), lookup_article, retrieve (date = event_date, không lọc lĩnh vực), refuse.
- [x] Task 5 — Nút grade (≤ 2 vòng viết lại), generate (gắn [chunk_id], KHÔNG_ĐỦ_CĂN_CỨ), verify (a) regex + (b) một lượt LLM theo cặp (câu, đoạn); câu mất hết căn cứ sinh lại 1 lần rồi gắn nhãn "chưa có căn cứ".
- [x] Task 6 — src/agent/graph.py: StateGraph, cạnh có điều kiện, baseline / full / no_router / no_grading / no_verify, trace {node, output, ms, llm_calls}. Xong khi: test đi đúng nhánh out_of_scope, direct, vòng viết lại dừng sau 2 lần, verify gỡ trích dẫn sai.
- [x] Task 7 — src/agent/run.py: Agent.run(question, config) theo Phụ lục A.5; CLI python -m src.agent.run "câu hỏi" --config full.
- [x] Task 8 — eval/agent_smoke.py: chạy thử 10 câu thật với Gemini, ghi lỗi prompt vào eval/results/agent_smoke.md, chỉnh prompt tối đa 2 vòng.

**Hoàng Sinh Hùng (chi tiết: docs/sprints/2026-10-16-sprint3-hung.md):**

- [x] Làm trước các thẻ Sprint 2 còn dở (ưu tiên H1, H2, H6).
- [x] H8 — Panel toàn văn Điều, tô sáng Khoản được trích (src/ui/article_view.py, sample_articles.json).
- [x] H9 — Hiển thị từ chối, nhãn "(chưa có căn cứ)", dòng tóm tắt từng bước trace; 3 phản hồi mẫu trong src/ui/samples/. → xong (giao diện NiceGUI, Sprint 4).
- [ ] ~~H10 — docs/judge_prompts.md~~ → thay bằng H10' (Sprint 4): duyệt prompt chấm trong eval/judge.py.: prompt chấm Faithfulness và Answer Correctness (0 / 0,5 / 1, đầu ra JSON) theo RAGAS (Đạt duyệt).
- [x] H11 — docs/rubric.md: thang chấm tay 3 mức kèm ví dụ và quy tắc biên. → xong (`docs/rubric.md`).
- [ ] ~~H12 — Bản nháp Chương 2 (BM25, dense, RRF, cross-encoder, RAG, Agentic-RAG, LangGraph, đặc thù văn bản luật).~~ → chuyển sang Sprint 5.

**Nghiệm thu sprint (28/10):** CLI trả lời đúng nhánh cho 4 loại câu hỏi; giao diện chạy với dữ liệu mẫu. Nếu tác tử chưa ổn định: áp dụng phương án dự phòng tại mục 11.

### SPRINT 4 (29/10 – 04/11/2026): TÍCH HỢP HỆ THỐNG VÀ ĐÁNH GIÁ CÂU TRẢ LỜI

**Mục tiêu sprint:** bản thử nghiệm chạy từ đầu đến cuối; pipeline đánh giá câu trả lời chạy được.

**Phạm Huỳnh Quốc Đạt (chi tiết: docs/superpowers/plans/2026-10-28-sprint4-dat.md):**

- [x] Task 1 — RQ4: chính sách lọc hiệu lực event / current / any (filters.ANY_DATE, date_policy trong state, Agent.run(question, config, date_policy)); route chịu được type không phải chuỗi.
- [x] Task 2 — eval/metrics.py: Citation P/R cấp Điều, tỷ lệ từ chối đúng, tỷ lệ đúng phiên bản (câu temporal).
- [x] Task 3 — eval/agent_eval.py run/report: chạy RQ3 (5 cấu hình; ablation trên mẫu phân tầng 60 câu) và RQ4 (12 câu temporal × 3 chính sách); ghi nối JSONL, chạy tiếp được, dừng êm khi hết quota.
- [x] Task 4 — eval/judge.py (Groq gpt-oss-120b, 1 lượt/câu, Faithfulness + Correctness 0 / 0,5 / 1; từ chối và câu ngoài phạm vi chấm bằng code); agent_eval judge/sheet/agree (phiếu chấm tay CSV, tỷ lệ khớp).
- [x] Task 5 — src/api/main.py: POST /api/ask (422 đầu vào sai, 503 LLM lỗi, phục vụ tuần tự), GET /api/article/{law_id}/{article}, GET /health; nạp mô hình một lần khi khởi động.
- [x] Task 6 — Chạy thử pipeline trên 10 câu RQ3 + 12 câu RQ4, đo quota thực tế, ghi lịch chạy đủ vào Sprint 5.
- [x] Chấm tay độc lập 20 câu trả lời (cùng Hùng, phiếu eval/results/grading_rq3.csv). → Đạt chấm một mình (`grading_rq3_dat.csv`), Hùng không chấm.

**Hoàng Sinh Hùng (chi tiết: docs/sprints/2026-10-28-sprint4-hung.md):**

- [x] Làm nốt thẻ Sprint 3: H9, H10' (duyệt prompt chấm trong eval/judge.py thay cho H10), H11, H12. → H9, H10', H11 xong; H12 chuyển sang Sprint 5.
- [x] H16 — Xem lại câu M_017 (đáp án mẫu dễ tranh cãi). → Hùng sửa câu hỏi, Đạt chạy lại 03/11.
- [x] H13 — Ghép giao diện với API (API_URL; không đặt thì dùng phản hồi mẫu), vòng chờ, thông báo lỗi; kiểm cùng Đạt. → xong (NiceGUI gọi API, kiểm 03/11).
- [x] H14 — Chấm tay độc lập 20 câu; tỷ lệ khớp người–LLM và giữa 2 người ghi vào docs/rubric.md. → Đạt chấm thay (khớp 0,950 / 0,917; kappa = 0).
- [x] H15 — Bản nháp Chương 1 (tổng quan đề tài). → xong (`docs/report/chuong1_draft.md`).

**Nghiệm thu sprint (04/11):** hỏi trên giao diện nhận câu trả lời thật kèm trích dẫn bấm được; evaluate.py chạy được trên 10 câu.

### SPRINT 5 (05/11 – 15/11/2026): THỰC NGHIỆM ĐẦY ĐỦ VÀ VIẾT BÁO CÁO

**Mục tiêu sprint:** số liệu RQ1–RQ4 đã đủ (chạy xong 03/11, gồm tập giữ riêng 30 câu); sprint này đo latency, phân tích lỗi, vẽ biểu đồ và viết bản nháp báo cáo khoảng 80%. Đóng băng tính năng ngày 12/11 (sau ngày này chỉ sửa lỗi).

**Phạm Huỳnh Quốc Đạt (chi tiết: docs/superpowers/plans/2026-11-05-sprint5-dat.md):**

- [x] Chạy đủ RQ3 (5 cấu hình × 209 câu), RQ4 (3 chính sách × 32 câu temporal), chấm Groq; chạy lại RQ1/RQ2 trên 77 câu Zalo; chạy lại M_017 sau khi Hùng sửa (H16).
- [x] Task 1 — API báo lỗi nhanh khi LLM quá tải (số lần thử lại của API giảm còn 2).
- [x] Task 2 — Điểm chấm gắn với câu trả lời đã chấm (`answer_sha`), không phải xóa tay dòng judge khi chạy lại.
- [x] Task 3 — Đo latency 20 câu không dùng cache (5 cấu hình), bảng trung vị/p90.
- [x] Task 4 — Phiếu phân tích lỗi 20 câu (`eval/error_analysis.py`); Đạt gán nhãn (thay H20 của Hùng) và lập bảng tổng hợp loại lỗi.
- [x] Task 5 — Biểu đồ RQ1–RQ4 (matplotlib) vào `docs/report/figures/`.
- [x] Task 6, 7 — Bản nháp Chương 3 (thiết kế hệ thống) và Chương 4 (thực nghiệm và kết quả).
- [x] Chương 2 Tổng quan tài liệu (thêm 10/11, `docs/report/chuong2_draft.md`): báo cáo thành 6 chương, các chương cũ 2–5 thành 3–6 và file `chuongN_draft.md` đổi tên theo. Các mục khác của sprint này giữ số chương cũ.

**Hoàng Sinh Hùng (chi tiết: docs/sprints/2026-11-05-sprint5-hung.md):**

- [x] H17 — Cập nhật số liệu Chương 1 (209 câu, tập giữ riêng, lịch mới). → Đạt làm thay (10/11).
- [x] H19 — Kiểm giao diện NiceGUI với API thật cùng Đạt (4 kịch bản demo). → Đạt kiểm 03/11 (4 kịch bản qua API + giao diện).
- [x] H18 — Sơ đồ use case và sequence. → Đạt làm thay (10/11), `assets/diagrams/usecase.*`, `sequence.*`.
- [x] H12 — Bản nháp Chương 2. → có bản nháp 06/11 (nay là `docs/report/chuong3_draft.md`), chưa rà.
- [x] H21 — Bản nháp Chương 5 (kết luận, hạn chế, hướng phát triển). → Đạt làm thay (10/11), nay là `docs/report/chuong6_draft.md`.

**Nghiệm thu sprint (15/11):** đủ bảng số liệu, latency, phân tích lỗi và biểu đồ RQ1–RQ4; bản nháp Chương 1–6.

### SPRINT 6 (16/11 – 27/11/2026): ĐÓNG GÓI VÀ HOÀN THIỆN

**Phạm Huỳnh Quốc Đạt (chi tiết: docs/superpowers/plans/2026-11-16-sprint6-dat.md):**

- [x] Task 1 — Sửa lỗi nhỏ ảnh hưởng người dùng/tái lập: JSONL ghi dở, `/api/article` phân biệt hoa thường, lỗi chỉ mục trả 500 dạng text, điểm chấm JSON hỏng không được chấm lại; xóa `eval/validate_chunks.py`.
- [ ] Task 2 — Dockerfile và docker-compose (dịch vụ api và ui, gắn chroma_db, cache mô hình, cache LLM). → đã chạy được; còn Đạt mở giao diện bằng trình duyệt kiểm một lần.
- [x] Task 3 — README: chạy bằng Docker, cài đặt, dữ liệu và chỉ mục, tái lập từng bảng số liệu RQ1–RQ4.
- [x] Task 4 — Dọn mã nguồn: lint lỗi pyflakes, xóa file thừa, toàn bộ kiểm thử đạt.
- [ ] Task 5 — Rà soát kỹ thuật toàn bộ báo cáo; kiểm tra Turnitin.

**Hoàng Sinh Hùng (chi tiết: docs/sprints/2026-11-16-sprint6-hung.md):**

- [ ] H22 — Giao diện bớt "kiểu AI" (bỏ nút đánh giá không lưu, gradient, hiệu ứng động; đổi nhãn; nhãn riêng khi dùng dữ liệu dự phòng); chụp lại ảnh.
- [ ] H23 — Ghép báo cáo theo mẫu TDTU (mục lục, danh mục hình và bảng, tóm tắt, tài liệu tham khảo APA).
- [ ] H24 — Slide bảo vệ (15–20 slide): vấn đề → câu hỏi nghiên cứu → kiến trúc → demo → kết quả RQ1–RQ4 → hạn chế và hướng phát triển.
- [ ] H25 — Video demo 3–5 phút với 4 kịch bản: câu tình huống, câu có mốc thời gian năm 2020, câu ngoài phạm vi bị từ chối, câu tra cứu trực tiếp điều luật.

**Cả hai:**

- [ ] 27/11: báo cáo hoàn chỉnh. 28/11–03/12: rà soát, dự phòng và tập dượt bảo vệ. 03/12: nộp repo kèm `chroma_db.zip` (hạn chót 23:59 04/12).
