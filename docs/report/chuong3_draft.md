# CHƯƠNG 3. CƠ SỞ LÝ THUYẾT

> **Bản nháp H12** — Hùng, 03/11/2026. Viết bằng Markdown để chép vào file báo cáo theo mẫu khoa.
> Quy ước trích dẫn: ưu tiên danh mục tài liệu tham khảo tại mục 12 đề cương. Các tài liệu nền tảng bổ trợ ngoài danh mục được gắn nhãn `[CẦN KIỂM TRA]` để đối chiếu trước khi hoàn thiện bản in.

Chương này trình bày toàn diện các cơ sở lý thuyết nền tảng, mô hình thuật toán và công nghệ then chốt được sử dụng để xây dựng hệ thống hỏi đáp pháp luật Việt Nam. Nội dung được bố cục thành 8 mục chính:
1. **3.1 Truy xuất thông tin từ vựng (Sparse Retrieval)**: Mô hình xác suất BM25 và xử lý từ khóa pháp lý tiếng Việt.
2. **3.2 Truy xuất dày đặc (Dense Retrieval)**: Nguyên lý Bi-encoder và mô hình biểu diễn đa ngôn ngữ BGE-M3.
3. **3.3 Kết hợp kết quả tìm kiếm: Reciprocal Rank Fusion (RRF)**: Kỹ thuật hợp nhất thứ hạng đa phương pháp không phụ thuộc điểm số.
4. **3.4 Xếp hạng lại bằng Cross-Encoder: Mô hình BGE-Reranker-v2-M3**: Cơ chế tương tác chéo từ tố và chiến lược truy xuất hai tầng.
5. **3.5 Kỹ thuật Retrieval-Augmented Generation (RAG)**: Kiến trúc sinh tăng cường truy xuất kinh điển và các thách thức trong bài toán pháp luật.
6. **3.6 Kiến trúc Agentic-RAG**: Tác tử tự trị với định tuyến thông minh, tự đánh giá bằng chứng, viết lại truy vấn và kiểm chứng trích dẫn hai lớp.
7. **3.7 Đồ thị trạng thái LangGraph**: Khung điều phối đồ thị có chu trình, quản lý trạng thái và rẽ nhánh có điều kiện.
8. **3.8 Đặc thù văn bản quy phạm pháp luật Việt Nam**: Cấu trúc phân cấp hình thức, hiện tượng nhầm lẫn văn bản (DRM) và nguyên tắc hiệu lực theo thời gian.

---

## 3.1 Truy xuất thông tin từ vựng (Sparse Retrieval)

### 3.1.1 Nguyên lý và mô hình xác suất

Truy xuất thông tin từ vựng (lexical / sparse retrieval) là phương pháp tìm kiếm dựa trên sự trùng khớp chính xác của các từ tố (tokens) giữa câu truy vấn và tập tài liệu. Trong số các mô hình từ vựng kinh điển, BM25 (Best Matching 25) do Robertson & Zaragoza (2009) hệ thống hóa trên nền tảng khung xác suất (Probabilistic Relevance Framework) là giải thuật chuẩn mực và hiệu quả bậc nhất.

Khác với mô hình không gian vector TF-IDF cơ bản vốn giả định độ liên quan tăng tuyến tính theo tần suất xuất hiện của từ, BM25 giải quyết hai vấn đề quan trọng trong thực tế:
1. **Sự bão hòa tần suất từ (Term Frequency Saturation):** Khi một từ xuất hiện nhiều lần trong một đoạn văn bản, mức độ đóng góp vào sự liên quan của từ đó sẽ tiệm cận một ngưỡng bão hòa thay vì tăng vô hạn.
2. **Chuẩn hóa độ dài tài liệu (Document Length Normalization):** Một đoạn văn bản dài có xu hướng chứa nhiều từ hơn, dẫn đến tần suất từ tự nhiên cao hơn mà không đồng nghĩa với việc nội dung của nó liên quan hơn đến truy vấn.

### 3.1.2 Công thức toán học của BM25

Cho một truy vấn $Q$ gồm các từ khóa $\{q_1, q_2, \dots, q_n\}$ và một tài liệu $D$ trong tập ngữ liệu gồm $N$ tài liệu, điểm số liên quan $Score_{BM25}(D, Q)$ được tính theo công thức:

$$Score_{BM25}(D, Q) = \sum_{i=1}^{n} IDF(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$

Trong đó:
- $f(q_i, D)$ là tần suất xuất hiện của từ khóa $q_i$ trong tài liệu $D$.
- $|D|$ là độ dài (tổng số từ) của tài liệu $D$, và $\text{avgdl}$ (average document length) là độ dài trung bình của toàn bộ các tài liệu trong kho dữ liệu.
- $k_1$ là tham số điều khiển mức độ bão hòa tần suất từ. Khi $k_1 = 0$, tần suất từ không còn ảnh hưởng đến điểm số; giá trị $k_1$ càng lớn thì ảnh hưởng của tần suất từ càng cao. Trong thực nghiệm thông thường, $k_1 \in [1.2, 2.0]$.
- $b$ là tham số điều khiển mức độ phạt đối với tài liệu dài. Nếu $b = 1$, mô hình chuẩn hóa độ dài tài liệu hoàn toàn; nếu $b = 0$, việc chuẩn hóa độ dài bị triệt tiêu hoàn toàn. Giá trị chuẩn mực thường được đặt là $b = 0.75$.
- $IDF(q_i)$ là trọng số nghịch đảo tần suất tài liệu (Inverse Document Frequency), đo lường mức độ cung cấp thông tin đặc trưng của từ $q_i$ trên toàn bộ kho ngữ liệu:

$$IDF(q_i) = \ln \left( \frac{N - n(q_i) + 0.5}{n(q_i) + 0.5} + 1 \right)$$

với $n(q_i)$ là số lượng tài liệu có chứa từ khóa $q_i$. Các từ xuất hiện quá phổ biến (ví dụ các hư từ hoặc từ thông dụng) sẽ có giá trị $IDF$ rất thấp, trong khi các thuật ngữ chuyên biệt có $IDF$ rất cao.

### 3.1.3 Ưu nhược điểm và vai trò trong hệ thống

- **Ưu điểm:** BM25 có tốc độ thực thi rất nhanh, chi phí tính toán thấp, không đòi hỏi huấn luyện tham số phức tạp trên GPU và bắt chính xác tuyệt đối các từ khóa chuyên biệt, mã điều luật hay các số hiệu văn bản (chẳng hạn như: `"Điều 357"`, `"Khoản 2"`, `"91/2015/QH13"`, `"bồi thường thiệt hại"`).
- **Hạn chế:** BM25 mắc phải vấn đề bất tương thích từ vựng (vocabulary mismatch problem). Nếu người dùng đặt câu hỏi bằng ngôn ngữ tự nhiên đời thường (ví dụ: *"công ty nợ lương kéo dài"*) mà trong điều luật lại sử dụng từ ngữ pháp lý chuẩn tắc (ví dụ: *"không được trả lương đầy đủ hoặc trả lương không đúng thời hạn"*), BM25 sẽ không thể nhận diện được sự tương đồng về mặt ý nghĩa do thiếu sự trùng lặp từ tố.
- **Vai trò trong hệ thống:** Trong hệ thống của đề tài (Chương 4), BM25 được sử dụng làm nhánh tìm kiếm từ vựng (sparse branch) trong kiến trúc tìm kiếm lai (Hybrid Search), kết hợp công cụ tách từ tiếng Việt Underthesea nhằm bảo đảm không bỏ sót các truy vấn tra cứu điều khoản trực tiếp hoặc các thuật ngữ pháp lý cố định.

---

## 3.2 Truy xuất dày đặc (Dense Retrieval)

### 3.2.1 Khái niệm Dense Retrieval và kiến trúc Bi-encoder

Để khắc phục nhược điểm bất tương thích từ vựng của phương pháp truyền thống, truy xuất dày đặc (Dense Retrieval) biểu diễn cả câu truy vấn và các đoạn văn bản thành các vector nhúng (embedding vectors) có số chiều cố định trong một không gian ngữ nghĩa liên tục đa chiều (thường từ 768 đến 1.024 chiều).

Kiến trúc chuẩn của Dense Retrieval là mô hình **Bi-encoder** (Hình 3.1):
- Hai bộ mã hóa (hoặc một bộ mã hóa dùng chung trọng số) nhận đầu vào là câu truy vấn $Q$ và tài liệu $D$ một cách độc lập để ánh xạ thành hai vector tương ứng $\vec{u} = \text{Encoder}(Q)$ và $\vec{v} = \text{Encoder}(D)$.
- Mức độ tương đồng ngữ nghĩa giữa truy vấn và tài liệu được tính toán nhanh chóng thông qua tích vô hướng (Dot Product) hoặc độ tương đồng Cosine:

$$Sim(Q, D) = \cos(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}$$

Nhờ sự phân tách độc lập này, toàn bộ kho văn bản quy phạm pháp luật có thể được mã hóa ngoại tuyến (offline pre-encoding) và lưu trữ dưới dạng các chỉ mục vector (vector index). Khi có truy vấn từ người dùng trong thời gian thực, hệ thống chỉ cần mã hóa câu hỏi và thực hiện thuật toán tìm kiếm láng giềng gần nhất (Approximate Nearest Neighbors - ANN) với độ trễ tính bằng mili-giây.

<!-- Hình 3.1: assets/diagrams/bi_encoder.png -->
**Hình 3.1.** Nguyên lý hoạt động của kiến trúc Bi-encoder trong Dense Retrieval.

### 3.2.2 Mô hình BGE-M3

Trong đề tài này, mô hình nhúng được lựa chọn là **BGE-M3** (Chen và cộng sự, 2024), một trong những mô hình nền tảng tiên tiến nhất hiện nay cho tác vụ biểu diễn văn bản. BGE-M3 nổi bật với ba đặc tính cốt lõi ("M3"):
1. **Multi-Lingual (Đa ngôn ngữ):** Mô hình được huấn luyện trên ngữ liệu khổng lồ gồm hơn 100 ngôn ngữ, hỗ trợ biểu diễn tiếng Việt với độ chính xác cao và hiểu sâu sắc mối quan hệ ngữ nghĩa trong văn phong tiếng Việt.
2. **Multi-Functionality (Đa tính năng):** BGE-M3 có khả năng đồng thời sinh ra biểu diễn vector dày (dense retrieval), biểu diễn trọng số từ vựng thưa (sparse retrieval) và biểu diễn đa vector tương tác muộn kiểu ColBERT. Trong phạm vi đề tài, nhóm khai thác tối đa tính năng dense embedding với vector 1.024 chiều.
3. **Multi-Granularity (Đa độ mịn):** BGE-M3 cho phép xử lý độ dài ngữ cảnh lên tới 8.192 token, giải quyết triệt để vấn đề mất thông tin khi nhúng các văn bản dài hoặc các điều luật nhiều khoản phức tạp.

Mô hình BGE-M3 được tối ưu hóa thông qua quy trình chưng cất tự tri thức (Self-Knowledge Distillation) kết hợp dữ liệu cặp câu hỏi - tài liệu quy mô lớn, giúp vector nhúng nắm bắt được các suy luận ngữ nghĩa phức tạp ngay cả khi cách diễn đạt giữa câu hỏi và câu trả lời hoàn toàn khác nhau.

### 3.2.3 Ưu nhược điểm và vai trò trong hệ thống

- **Ưu điểm:** Khả năng hiểu ngữ nghĩa vượt trội, tìm được các điều luật tương ứng với câu hỏi tình huống đời thường của người dân ngay cả khi không có từ ngữ trùng khớp.
- **Hạn chế:** Dễ gặp hiện tượng ảo tưởng ngữ nghĩa (semantic drift) đối với các chi tiết mang tính định lượng tuyệt đối, chẳng hạn như phân biệt giữa `"30 ngày"` và `"45 ngày"`, hoặc giữa `"Điều 20"` và `"Điều 22"`. Ngoài ra, chi phí tính toán bộ nhớ và CPU cao hơn so với tìm kiếm từ vựng.
- **Vai trò trong hệ thống:** BGE-M3 đóng vai trò là động cơ cốt lõi cho chỉ mục vector trong ChromaDB, phụ trách nhánh tìm kiếm ngữ nghĩa (dense branch) nhằm đảm bảo tỷ lệ bao phủ (Recall) cao cho các câu hỏi tình huống thực tế (Chương 4).

---

## 3.3 Kết hợp kết quả tìm kiếm: Reciprocal Rank Fusion (RRF)

### 3.3.1 Vấn đề bất đồng nhất điểm số giữa các hệ thống truy xuất

Khi kết hợp tìm kiếm từ vựng (BM25) và tìm kiếm dày đặc (Dense), thách thức lớn nhất là sự khác biệt về bản chất của điểm số liên quan:
- Điểm BM25 là điểm số không giới hạn trên (unbounded score), phụ thuộc vào độ dài tài liệu, tần suất từ và kích thước kho dữ liệu.
- Điểm tương đồng của Dense Retrieval (như Cosine similarity) nằm trong đoạn $[-1, 1]$ hoặc $[0, 1]$, có phân phối xác suất hoàn toàn khác biệt.

Nếu áp dụng phương pháp cộng điểm tuyến tính có trọng số $\alpha \cdot Score_{\text{BM25}} + (1 - \alpha) \cdot Score_{\text{Dense}}$, hệ thống đòi hỏi phải chuẩn hóa điểm số (score normalization) cực kỳ phức tạp, đồng thời rất nhạy cảm với việc chọn tham số $\alpha$, dễ dẫn đến suy giảm độ chính xác khi phân phối câu hỏi thay đổi.

### 3.3.2 Thuật toán Reciprocal Rank Fusion (RRF)

Để giải quyết vấn đề trên, Cormack và cộng sự (2009) đề xuất kỹ thuật **Reciprocal Rank Fusion (RRF)**. Nguyên lý cốt lõi của RRF là: **chỉ sử dụng vị trí thứ hạng (rank) của tài liệu trong từng danh sách kết quả thay vì sử dụng điểm số tuyệt đối**.

Cho một tập hợp các phương pháp truy xuất $M$ (trong hệ thống của đề tài, $M = \{\text{BM25}, \text{Dense}\}$), mỗi phương pháp $m \in M$ trả về một danh sách các tài liệu được sắp xếp theo thứ tự giảm dần của độ liên quan. Với mỗi tài liệu $d$, thứ hạng của nó trong danh sách của phương pháp $m$ được ký hiệu là $r_m(d) \in \{1, 2, 3, \dots\}$.

Điểm số RRF tổng hợp của tài liệu $d$ được tính bằng công thức:

$$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Trong đó:
- $r_m(d)$ là vị trí thứ hạng của tài liệu $d$ theo phương pháp $m$. Nếu tài liệu $d$ không xuất hiện trong danh sách trả về của phương pháp $m$, giá trị nghịch đảo coi như bằng $0$.
- $k$ là một hằng số làm mịn (smoothing constant). Hằng số này có vai trò giảm thiểu sự chênh lệch quá mức giữa các vị trí đứng đầu (ví dụ thứ hạng 1 và 2) và ổn định thứ hạng của các tài liệu xuất hiện ở nhóm sau. Trong thực nghiệm gốc của Cormack và cộng sự (2009) cũng như các nghiên cứu chuẩn mực, giá trị $k = 60$ được chứng minh là cho kết quả tối ưu và ổn định nhất.

### 3.3.3 Vai trò trong hệ thống

Nguyen Ba và cộng sự (2024) cho thấy tìm kiếm lai bằng một biến thể chuẩn hóa của RRF đạt Recall cao hơn từng nhánh đơn lẻ trên dữ liệu pháp luật tiếng Việt. Trong kiến trúc của đề tài, RRF hợp nhất 50 ứng viên từ mỗi nhánh BM25 và Dense, rồi 10 đoạn đứng đầu được đưa sang bước xếp hạng lại (mục 4.3).

---

## 3.4 Xếp hạng lại bằng Cross-Encoder: Mô hình BGE-Reranker-v2-M3

### 3.4.1 So sánh Bi-Encoder và Cross-Encoder

Mặc dù mô hình Bi-encoder cho phép tìm kiếm nhanh chóng nhờ vector hóa độc lập, nhược điểm chí mạng của nó là hai chuỗi văn bản (truy vấn và tài liệu) không có cơ hội tương tác trực tiếp ở cấp độ từ tố (token-level interaction) trong quá trình tính toán vector nhúng. Điều này dẫn đến việc bỏ sót các mối liên kết ngữ nghĩa tinh tế hoặc các sắc thái phủ định, điều kiện loại trừ vốn rất phổ biến trong văn bản pháp luật.

Mô hình **Cross-Encoder** khắc phục triệt để nhược điểm này (Hình 3.2). Trong Cross-Encoder:
- Câu truy vấn $Q$ và đoạn văn bản ứng viên $D$ được ghép nối thành một chuỗi duy nhất:
  $$\text{Input} = [CLS] \circ q_1 \dots q_n \circ [SEP] \circ d_1 \dots d_m \circ [SEP]$$
- Chuỗi kết hợp được đưa đồng thời qua toàn bộ các lớp Transformer Self-Attention. Tại mọi tầng của mạng nơ-ron, từng từ tố của câu hỏi đều có thể đối chiếu chéo (cross-attend) trực tiếp với từng từ tố của điều luật.
- Vector ẩn tại vị trí đầu $[CLS]$ được đưa qua một lớp phân loại tuyến tính để tính ra điểm số liên quan duy nhất $Score_{\text{Cross}}(Q, D) \in [0, 1]$.

<!-- Hình 3.2: assets/diagrams/cross_encoder.png -->
**Hình 3.2.** So sánh cơ chế tương tác giữa Bi-Encoder và Cross-Encoder.

**Bảng 3.1.** So sánh đặc tính kỹ thuật giữa Bi-Encoder và Cross-Encoder.

| Đặc tính | Bi-Encoder (BGE-M3) | Cross-Encoder (BGE-Reranker-v2-M3) |
|---|---|---|
| **Cơ chế biểu diễn** | Mã hóa độc lập $Q$ và $D$ | Mã hóa liên hợp chuỗi $[Q; D]$ |
| **Tương tác từ tố** | Không có (chỉ tính tích vô hướng ở tầng cuối) | Toàn phần qua các lớp Self-Attention |
| **Khả năng tiền lập chỉ mục** | Có (tính toán offline toàn bộ kho luật) | Không thể (bắt buộc phải tính khi có cặp $Q, D$) |
| **Độ phức tạp tính toán** | Thấp khi tìm kiếm ($O(N \cdot d)$) | Rất cao ($O(K \cdot L^2)$ với $K$ là số ứng viên) |
| **Độ chính xác phân loại** | Khá cao, đóng vai trò chọn lọc diện rộng | Cực kỳ cao, loại bỏ nhiễu ngữ nghĩa triệt để |

### 3.4.2 Mô hình BGE-Reranker-v2-M3 và chiến lược hai tầng (Two-stage Retrieval)

Do chi phí tính toán của Cross-Encoder rất lớn, việc áp dụng mô hình này trực tiếp lên hàng nghìn điều khoản trong toàn bộ kho luật là bất khả thi về mặt thời gian đáp ứng thực tế. Vì vậy, giải pháp chuẩn mực trong xử lý ngôn ngữ hiện đại là áp dụng **chiến lược truy xuất hai tầng (Two-stage Retrieval Pipeline)**:
1. **Tầng 1 (First-stage Retrieval / Filtering):** Sử dụng tìm kiếm lai BM25 + Dense kết hợp RRF để quét nhanh toàn bộ kho dữ liệu, thu hẹp phạm vi từ hàng nghìn điều khoản xuống còn một tập ứng viên nhỏ ($K = 10$; 20 ứng viên mất khoảng 11 giây mỗi câu trên CPU, mục 4.3).
2. **Tầng 2 (Second-stage Reranking):** Sử dụng mô hình Cross-Encoder chuyên dụng `bge-reranker-v2-m3` để chấm điểm và tái sắp xếp 10 đoạn ứng viên này, chỉ giữ lại 5 đoạn có chất lượng cao nhất đưa vào ngữ cảnh mô hình ngôn ngữ.

Mô hình `bge-reranker-v2-m3` là mô hình xếp hạng lại đa ngôn ngữ nhẹ nhưng có hiệu năng phân loại vượt trội, đặc biệt nhạy bén trong việc xác định xem đoạn trích dẫn có thực sự trả lời đúng trọng tâm câu hỏi hay chỉ chứa các từ ngữ liên quan về mặt chủ đề.

---

## 3.5 Kỹ thuật Retrieval-Augmented Generation (RAG)

### 3.5.1 Khái niệm và kiến trúc RAG kinh điển

Mô hình ngôn ngữ lớn (LLMs) tuy sở hữu khả năng diễn đạt ngôn ngữ tự nhiên xuất sắc nhưng tri thức của chúng bị đóng băng tại thời điểm huấn luyện (parametric memory), đồng thời thường xuyên gặp hiện tượng ảo giác (hallucination) — tức tự tạo ra các thông tin sai lệch nhưng với giọng văn hết sức tự tin. Trong lĩnh vực tư vấn pháp lý, ảo giác là sai phạm không thể chấp nhận được vì có thể dẫn tới những hậu quả nghiêm trọng về mặt quyền lợi và nghĩa vụ công dân.

Kỹ thuật **Retrieval-Augmented Generation (RAG)** do Lewis và cộng sự (2020) đề xuất nhằm kết hợp bộ nhớ tham số của LLM với kho tri thức phi tham số (non-parametric memory) bên ngoài. Kiến trúc RAG chuẩn mực gồm hai phân hệ:
1. **Bộ truy xuất (Retriever):** Tiếp nhận câu hỏi $Q$ từ người dùng, tìm kiếm trong kho tri thức và trích xuất ra một tập hợp $k$ đoạn ngữ cảnh liên quan $C = \{c_1, c_2, \dots, c_k\}$.
2. **Bộ sinh (Generator):** Nhận đầu vào là câu hỏi kết hợp với ngữ cảnh được truy xuất để sinh ra câu trả lời $A$ dựa trên phân phối xác suất có điều kiện:

$$P(A | Q) = \prod_{t=1}^{T} P(a_t | a_{<t}, Q, C)$$

<!-- Hình 3.3: assets/diagrams/naive_rag.png -->
**Hình 3.3.** Quy trình tuyến tính một lượt của hệ thống RAG truyền thống (Naive RAG).

### 3.5.2 Hạn chế của RAG truyền thống trong bài toán pháp luật

Mặc dù giải quyết được một phần hiện tượng ảo giác, mô hình RAG truyền thống dạng đường ống tuyến tính một lượt (Naive RAG) bộc lộ nhiều điểm nghẽn nghiêm trọng khi áp dụng vào lĩnh vực pháp luật:
- **Thiếu khả năng tự phê bình (Garbage In, Garbage Out):** Nếu khâu truy xuất trả về các điều luật không liên quan hoặc chỉ liên quan một phần, bộ sinh LLM vẫn bị ép buộc phải sinh câu trả lời dựa trên các dữ liệu sai lệch đó, dẫn đến câu trả lời sai hoặc lạc đề.
- **Không phân biệt được phạm vi tri thức:** RAG truyền thống không thể nhận diện được các câu hỏi nằm ngoài phạm vi kho văn bản hoặc các câu hỏi không có cơ sở pháp lý tương ứng để từ chối trả lời, mà luôn cố gắng suy diễn.
- **Trích dẫn giả và trích dẫn không hỗ trợ (Unsupported Citations):** Gao và cộng sự (2023) trong nghiên cứu về khung đánh giá ALCE đã chỉ ra rằng ngay cả các mô hình LLM tiên tiến nhất vẫn thường xuyên tạo ra các trích dẫn sai nguồn, hoặc trích dẫn những điều luật không chứa đựng nội dung hỗ trợ cho khẳng định trong câu trả lời.
- **Bất lực trước câu hỏi nhiều bước hoặc câu hỏi tra cứu trực tiếp:** Các câu hỏi tra cứu đích danh số hiệu điều luật đòi hỏi truy xuất chính xác tuyệt đối, trong khi các câu hỏi tình huống phức tạp lại đòi hỏi viết lại truy vấn để bóc tách vấn đề, điều mà đường ống một lượt không thể đảm đương.

---

## 3.6 Kiến trúc Agentic-RAG

### 3.6.1 Từ RAG thụ động đến Tác tử Agentic-RAG

Để vượt qua giới hạn của RAG truyền thống, xu hướng nghiên cứu chuyển dịch mạnh mẽ sang **Agentic-RAG** (Hình 3.4). Một tác tử thông minh (agent) là một thực thể tính toán có khả năng:
- **Tự nhận thức trạng thái (State Awareness):** Duy trì và theo dõi ngữ cảnh hội thoại, lịch sử truy xuất và chất lượng bằng chứng hiện có.
- **Sử dụng công cụ (Tool Use):** Tự quyết định gọi các công cụ chuyên biệt khi cần (như công cụ tra cứu văn bản, công cụ tìm kiếm lai, công cụ lọc thời gian).
- **Lập luận và phản tỉnh (Reflection & Reasoning):** Tự đánh giá kết quả trung gian, phát hiện điểm thiếu sót và tự động thực hiện các hành động khắc phục trước khi đưa ra phản hồi cuối cùng cho người dùng.

<!-- Hình 3.4: assets/diagrams/agentic_rag.png -->
**Hình 3.4.** Luồng điều phối thông minh của Agentic-RAG so với RAG truyền thống.

### 3.6.2 Các cơ chế thành phần trong hệ thống Agentic-RAG

Hệ thống Agentic-RAG trong đề tài kế thừa và tích hợp các kỹ thuật tiên tiến sau:

#### 1. Định tuyến câu hỏi (Query Routing)
Trước khi thực hiện truy xuất, tác tử phân tích ý định của người dùng để phân loại câu hỏi thành các nhóm:
- *Tra cứu trực tiếp (direct lookup):* Người dùng nêu rõ tên văn bản và số hiệu điều luật (ví dụ: *"Điều 20 Bộ luật Lao động 2019 quy định gì?"*). Tác tử gọi trực tiếp công cụ đọc văn bản mà không cần qua tìm kiếm vector.
- *Câu hỏi tình huống (situational):* Tình huống thực tế cần phân tích căn cứ pháp lý. Tác tử đồng thời trích xuất mốc thời gian xảy ra sự việc (nếu có) để phục vụ lọc hiệu lực.
- *Câu hỏi ngoài phạm vi (out-of-scope):* Các câu hỏi không thuộc 4 lĩnh vực luật được quản lý hoặc các câu chào hỏi xã giao. Tác tử kích hoạt cơ chế từ chối trả lời lịch sự ngay từ đầu, tiết kiệm chi phí tính toán.

#### 2. Tự đánh giá bằng chứng và viết lại truy vấn (Self-Grading & Query Rewriting)
Bước này kế thừa ý tưởng tự đánh giá bằng chứng của Corrective RAG (Yan và cộng sự, 2024) và Self-RAG (Asai và cộng sự, 2024), đã trình bày ở mục 2.3, và được hiện thực bằng prompt có cấu trúc trên đồ thị trạng thái.

Sau khi truy xuất, một nút đánh giá (Grader) kiểm tra xem các đoạn văn bản luật thu được có chứa đầy đủ điều kiện để giải quyết tình huống hay không. Nếu bằng chứng còn thiếu hoặc mơ hồ, tác tử sẽ tự động phân tích lỗ hổng thông tin, viết lại câu truy vấn (Query Rewriter) với các thuật ngữ chuyên sâu hơn và thực hiện truy xuất bổ sung (tối đa 2 vòng lặp).

#### 3. Kiểm chứng trích dẫn hai lớp (Two-tier Citation Verification)
Để kiểm soát độ tin cậy của trích dẫn, đề tài thiết kế cơ chế kiểm chứng trích dẫn chuyên biệt gồm hai lớp:
1. **Lớp 1 – Kiểm chứng cú pháp và nguồn gốc (Syntactic & Lexical Verification):** Sử dụng các biểu thức chính quy (Regex) quét toàn bộ các mã định danh trích dẫn xuất hiện trong câu trả lời (dạng `[LAW_DieuX_KhoanY]`). Đối chiếu danh sách này với tập hợp các đoạn chunk thực tế đã được cung cấp trong ngữ cảnh truy xuất. Bất kỳ trích dẫn nào trỏ tới một điều luật không có trong ngữ cảnh sẽ bị loại bỏ ngay lập tức (chống hiện tượng bịa mã luật).
2. **Lớp 2 – Kiểm chứng ngữ nghĩa và mức độ hỗ trợ (Semantic Entailment Verification):** Áp dụng mô hình ngôn ngữ lớn để thực hiện kiểm tra chéo từng cặp khẳng định - căn cứ trích dẫn (claim-to-citation entailment). Đối với mỗi câu khẳng định pháp lý, LLM xác định xem nội dung điều khoản được trích có thực sự hỗ trợ (entails) cho khẳng định đó hay không:
   - Nếu trích dẫn hỗ trợ đúng: giữ nguyên.
   - Nếu trích dẫn không liên quan hoặc hiểu sai ngữ nghĩa: loại bỏ thẻ trích dẫn hoặc cảnh báo câu chưa có căn cứ vững chắc.

Cơ chế này nhằm loại các trích dẫn bịa mã hoặc không được đoạn luật hỗ trợ; hiệu quả thực tế được đo ở mục 5.4.3 (phép thử tiêm trích dẫn sai) và mục 5.6 (phân tích lỗi).

---

## 3.7 Đồ thị trạng thái LangGraph

### 3.7.1 Hạn chế của các framework chuỗi tuyến tính (Linear Chains)

Trong các hệ thống xây dựng ứng dụng LLM thế hệ đầu (chẳng hạn như LangChain Chains truyền thống), luồng thực thi được thiết kế dưới dạng đồ thị có hướng không chu trình tuyến tính (DAG). Dạng kiến trúc này chỉ phù hợp cho các chuỗi xử lý một chiều tuần tự: `Prompt -> LLM -> OutputParser`.

Tuy nhiên, như đã phân tích ở mục 3.6, một tác tử Agentic-RAG hoàn chỉnh bắt buộc phải có khả năng:
- Tạo vòng lặp có điều kiện (conditional loops) để truy xuất lại khi bằng chứng chưa đạt yêu cầu.
- Rẽ nhánh động (dynamic branching) dựa trên quyết định của bộ định tuyến.
- Lưu giữ và cập nhật một trạng thái bộ nhớ chung (shared mutable state) liên tục xuyên suốt các bước thực thi.

### 3.7.2 Nguyên lý hoạt động của LangGraph

LangGraph là khung thư viện mở rộng từ hệ sinh thái LangChain, được thiết kế chuyên biệt để xây dựng các hệ thống tác tử phức tạp dựa trên mô hình **Đồ thị trạng thái có chu trình (Cyclic State Graph)**.

Ba thành phần kiến trúc cơ bản của LangGraph bao gồm:
1. **Trạng thái đồ thị (State):** Là một đối tượng dữ liệu có cấu trúc (thường kế thừa từ `typing.TypedDict` hoặc Pydantic) đại diện cho bộ nhớ trung tâm của tác tử. Mọi nút trong đồ thị đều đọc thông tin từ trạng thái này và trả về các cập nhật để ghi đè hoặc bổ sung vào trạng thái.
   - Trong đề tài, State lưu trữ: câu hỏi ban đầu, phân loại ý định, mốc thời gian sự việc, danh sách đoạn luật truy xuất được, số lần lặp truy xuất, câu trả lời thô và kết quả kiểm chứng trích dẫn.
2. **Các Nút (Nodes):** Đại diện cho các hàm tính toán xử lý logic độc lập hoặc các lời gọi công cụ. Mỗi nút nhận `State` hiện tại làm tham số đầu vào và trả về một phần dữ liệu cập nhật cho `State`. Ví dụ các nút: `route`, `lookup_article`, `retrieve`, `grade`, `generate`, `verify`.
3. **Các Cạnh (Edges) và Cạnh có điều kiện (Conditional Edges):**
   - *Cạnh cố định (Normal Edge):* Nối trực tiếp từ một nút đến một nút kế tiếp xác định (ví dụ: sau khi `generate` luôn chuyển tiếp sang `verify`).
   - *Cạnh có điều kiện (Conditional Edge):* Là một hàm điều kiện (router function) nhận `State` hiện tại và trả về tên nút tiếp theo cần chuyển dịch. Ví dụ: hàm kiểm tra sau nút `grade` sẽ phân nhánh: nếu tài liệu đạt yêu cầu thì chuyển sang `generate`; nếu chưa đạt và số vòng lặp $retry < 2$ thì chuyển ngược lại nút `retrieve`; nếu đã quá số lần lặp thì chuyển sang chế độ trả lời giới hạn kèm cảnh báo.

```
       [Start]
          │
          ▼
       [route] ────────── (out_of_scope) ──────────► [refuse] ──┐
          │                                                      │
     (situational)                                               │
          │                                                      │
          ▼                                                      │
    [retrieve] ◄──────────────┐                                  │
          │                   │                                  │
          ▼                   │ (not relevant & retry < 2)       │
       [grade] ───────────────┘                                  │
          │                                                      │
     (relevant)                                                  │
          │                                                      │
          ▼                                                      │
     [generate]                                                  │
          │                                                      │
          ▼                                                      │
      [verify] ──────────────────────────────────────────────────┴──► [End]
```
<!-- Hình 3.5: assets/diagrams/langgraph_flow.png -->
**Hình 3.5.** Sơ đồ chuyển dịch trạng thái đồ thị LangGraph trong tác tử hỏi đáp pháp luật.

### 3.7.3 Vai trò trong hệ thống

LangGraph cung cấp cấu trúc rõ ràng, tính kiểm thử cao (testability), khả năng truy vết hoàn chỉnh từng bước thực thi (traceability) và cho phép dễ dàng bật/tắt các thành phần độc lập thông qua các cờ cấu hình nhằm phục vụ trực tiếp cho nghiên cứu lược bỏ (Ablation Study) trong RQ3 (Chương 4, Chương 5).

---

## 3.8 Đặc thù văn bản quy phạm pháp luật Việt Nam

### 3.8.1 Cấu trúc phân cấp hình thức và hiện tượng Document-Level Retrieval Mismatch (DRM)

Văn bản quy phạm pháp luật Việt Nam tuân theo cấu trúc phân cấp nghiêm ngặt được quy định bởi Luật Ban hành văn bản quy phạm pháp luật:
$$\text{Văn bản} \longrightarrow \text{Phần} \longrightarrow \text{Chương} \longrightarrow \text{Mục} \longrightarrow \text{Điều} \longrightarrow \text{Khoản} \longrightarrow \text{Điểm}$$

Mỗi đơn vị quy phạm hoàn chỉnh thường là một **Khoản** hoặc một **Điều**. Nếu áp dụng kỹ thuật phân đoạn cố định theo số lượng từ (Fixed-size Chunking) phổ biến trong các ứng dụng RAG thông thường (ví dụ: cắt cứng 300 từ kèm chồng lấp 50 từ), sẽ xảy ra hai vấn đề nghiêm trọng:
1. **Làm đứt đoạn quy phạm pháp luật:** Một câu văn chứa điều kiện áp dụng ở đầu Điều có thể bị cắt rời khỏi chế tài xử lý ở cuối Điều, khiến mô hình ngôn ngữ hiểu sai bản chất quy định.
2. **Mất ngữ cảnh nguồn gốc và hiện tượng DRM:** Reuter và cộng sự (2025) chỉ ra rằng trong kho văn bản pháp luật lớn, có rất nhiều điều khoản thuộc các văn bản luật khác nhau có tiêu đề và cách diễn đạt tương đồng (ví dụ: điều khoản về *"Thời giờ làm việc"*, *"Hợp đồng vô hiệu"*, *"Quyền của người lao động"*). Khi một đoạn văn bản bị tách rời khỏi tiêu đề Chương và tên Văn bản, mô hình tìm kiếm rất dễ truy xuất nhầm đoạn văn từ một văn bản luật khác điều chỉnh cùng chủ đề nhưng không đúng đối tượng áp dụng. Đây gọi là hiện tượng **Document-Level Retrieval Mismatch (DRM)**.

Để khắc phục hiện tượng này, kỹ thuật phân đoạn cấu trúc kèm bổ sung tiêu đề phân cấp (Hierarchy-enriched chunking) được áp dụng: mỗi đoạn trích cấp Khoản đều được ghép nối với thông tin phân cấp hoàn chỉnh:
$$\text{Context Header} = \text{[Tên Văn bản]} > \text{[Chương]} > \text{[Điều X: Tên Điều]} > \text{[Khoản Y]}$$
Kỹ thuật này giúp bảo toàn trọn vẹn ngữ cảnh độc lập của từng đoạn luật khi nạp vào chỉ mục vector, hạn chế tối đa hiện tượng nhầm lẫn văn bản (được đánh giá định lượng tại RQ2).

### 3.8.2 Hiệu lực pháp luật theo thời gian (Temporal Validity)

Nguyên tắc pháp lý phổ quát quy định rằng: **Hành vi pháp lý hoặc sự kiện pháp lý xảy ra tại thời điểm nào thì phải áp dụng văn bản quy phạm pháp luật đang có hiệu lực thi hành tại thời điểm đó** (trừ trường hợp pháp luật có quy định hồi tố).

Trong thực tế xây dựng kho dữ liệu pháp luật, các văn bản luật luôn biến động theo thời gian:
- Một luật mới ra đời sẽ bãi bỏ hoặc thay thế một hoặc nhiều luật cũ (ví dụ: Bộ luật Lao động 2019 có hiệu lực từ 01/01/2021 đã bãi bỏ hoàn toàn Bộ luật Lao động 2012).
- Các điều khoản cụ thể có sự thay đổi căn bản về mặt quyền lợi và nghĩa vụ. Chẳng hạn:
  - *Bộ luật Lao động 2012 (Điều 22):* Cho phép giao kết hợp đồng lao động theo mùa vụ hoặc theo một công việc nhất định có thời hạn dưới 12 tháng.
  - *Bộ luật Lao động 2019 (Điều 20):* Bãi bỏ hoàn toàn loại hợp đồng mùa vụ, chỉ công nhận hai loại hợp đồng: xác định thời hạn và không xác định thời hạn.
  - *Quyền đơn phương chấm dứt hợp đồng của người lao động:* Theo luật 2012 (Điều 37), người lao động làm hợp đồng xác định thời hạn bắt buộc phải có lý do luật định; trong khi theo luật 2019 (Điều 35), người lao động có quyền nghỉ việc không cần lý do, chỉ cần đáp ứng thời hạn báo trước.

Nếu một người dùng hỏi: *"Năm 2019, tôi ký hợp đồng lao động theo mùa vụ thì thời hạn tối đa là bao lâu?"*, hệ thống chỉ lưu trữ văn bản hiện hành (Bộ luật Lao động 2019) sẽ đưa ra câu trả lời rằng luật hiện nay không có hợp đồng mùa vụ, dẫn đến kết luận sai lệch bản chất pháp lý của sự việc đã diễn ra trong quá khứ.

Để xử lý bài toán này, mỗi văn bản luật $L$ trong kho dữ liệu được gán nhãn một khoảng hiệu lực thời gian xác định $[d_{\text{effective}}, d_{\text{expiry}})$. Khi tiếp nhận câu hỏi có chứa mốc thời gian sự việc $d_{\text{event}}$, điều kiện ràng buộc lọc hiệu lực được định nghĩa chặt chẽ như sau:

$$d_{\text{effective}} \le d_{\text{event}} < d_{\text{expiry}}$$

Chỉ những văn bản thỏa mãn bất đẳng thức trên mới được đưa vào phạm vi tìm kiếm của bộ truy xuất. Đây chính là cơ sở lý luận để nhóm thiết kế các bộ lọc siêu dữ liệu (metadata filtering) và xây dựng tập câu hỏi thực nghiệm nhằm trả lời câu hỏi nghiên cứu RQ4 (Chương 4, Chương 5).

---

## 3.9 Tóm tắt chương

Chương 3 đã hệ thống hóa toàn diện các cơ sở lý thuyết và công nghệ nền tảng tạo nên sức mạnh cho hệ thống hỏi đáp pháp luật Việt Nam:
1. **Truy xuất thông tin đa phương pháp:** Kết hợp sức mạnh từ khóa chính xác của mô hình xác suất **BM25** với khả năng nắm bắt ngữ nghĩa sâu của mô hình **BGE-M3 (Dense)** thông qua thuật toán hợp nhất thứ hạng **RRF**, sau đó tinh lọc bằng mô hình xếp hạng lại **Cross-Encoder (BGE-Reranker-v2-M3)**.
2. **Kiến trúc tác tử thông minh Agentic-RAG:** Vượt qua giới hạn thụ động của RAG truyền thống nhờ các cơ chế định tuyến thông minh, tự đánh giá và truy xuất lại lặp vòng (Self-Grading & Rewriting), kết hợp quy trình kiểm chứng trích dẫn hai lớp chặt chẽ.
3. **Môi trường điều phối LangGraph:** Cho phép mô hình hóa luồng tác tử dưới dạng đồ thị trạng thái có chu trình, minh bạch, kiểm soát luồng tối ưu và hỗ trợ thực hiện các thực nghiệm lược bỏ.
4. **Mô hình hóa đặc thù pháp luật Việt Nam:** Đề xuất phương pháp phân đoạn bảo toàn cấu trúc phân cấp để giảm hiện tượng nhầm lẫn văn bản (DRM), đồng thời thiết lập cơ chế lọc văn bản theo khoảng thời gian hiệu lực tại thời điểm phát sinh sự việc.

Toàn bộ các nền tảng lý thuyết này là kim chỉ nam trực tiếp định hình nên thiết kế chi tiết và quy trình cài đặt hệ thống được trình bày cụ thể trong Chương 4 tiếp theo.
