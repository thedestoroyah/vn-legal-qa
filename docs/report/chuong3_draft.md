# CHƯƠNG 3. CƠ SỞ LÝ THUYẾT

> **Bản nháp H12** — Hùng, 03/11/2026; Đạt rà lại 16/11 (bỏ từ cường điệu, đối chiếu với code, thêm trích dẫn).
> Chỉ trích tài liệu có trong `tai_lieu_tham_khao.md`; tham số nêu trong chương phải khớp với Chương 4 và mã nguồn.

Chương này trình bày cơ sở lý thuyết của các kỹ thuật được dùng trong hệ thống, gồm 8 mục:
1. **3.1 Truy xuất từ vựng (Sparse Retrieval)**: mô hình xác suất BM25.
2. **3.2 Truy xuất dày đặc (Dense Retrieval)**: kiến trúc bi-encoder và mô hình BGE-M3.
3. **3.3 Reciprocal Rank Fusion (RRF)**: hợp nhất thứ hạng của nhiều phương pháp truy xuất.
4. **3.4 Xếp hạng lại bằng cross-encoder**: mô hình BGE-Reranker-v2-M3 và truy xuất hai tầng.
5. **3.5 Retrieval-Augmented Generation (RAG)**: kiến trúc RAG một lượt và hạn chế trong bài toán pháp luật.
6. **3.6 Agentic-RAG**: định tuyến câu hỏi, tự đánh giá bằng chứng, viết lại truy vấn và kiểm chứng trích dẫn hai lớp.
7. **3.7 Đồ thị trạng thái LangGraph**: điều phối tác tử bằng đồ thị có chu trình.
8. **3.8 Đặc thù văn bản pháp luật Việt Nam**: cấu trúc phân cấp, truy xuất nhầm văn bản (DRM) và hiệu lực theo thời gian.

---

## 3.1 Truy xuất thông tin từ vựng (Sparse Retrieval)

### 3.1.1 Nguyên lý và mô hình xác suất

Truy xuất từ vựng (lexical hay sparse retrieval) tìm tài liệu dựa trên sự trùng khớp từ tố (token) giữa câu truy vấn và tài liệu. BM25 (Best Matching 25), được Robertson và Zaragoza (2009) trình bày trong khung xác suất về độ liên quan (Probabilistic Relevance Framework), là mô hình từ vựng được dùng phổ biến nhất hiện nay.

So với TF-IDF cơ bản, trong đó điểm tăng tuyến tính theo tần suất từ, BM25 xử lý thêm hai hiện tượng:
1. **Bão hòa tần suất từ (term frequency saturation):** một từ lặp lại nhiều lần trong đoạn văn chỉ làm điểm tăng tới một ngưỡng, không tăng mãi.
2. **Chuẩn hóa độ dài tài liệu (document length normalization):** đoạn văn dài tự nhiên chứa nhiều lần xuất hiện của từ hơn, nhưng không vì thế mà liên quan hơn.

### 3.1.2 Công thức toán học của BM25

Cho truy vấn $Q$ gồm các từ $\{q_1, q_2, \dots, q_n\}$ và tài liệu $D$ trong kho gồm $N$ tài liệu, điểm liên quan được tính theo công thức (Robertson và Zaragoza, 2009):

$$Score_{BM25}(D, Q) = \sum_{i=1}^{n} IDF(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$

Trong đó:
- $f(q_i, D)$ là số lần từ $q_i$ xuất hiện trong $D$.
- $|D|$ là độ dài (số từ) của $D$; $\text{avgdl}$ là độ dài trung bình của các tài liệu trong kho.
- $k_1$ điều khiển mức bão hòa: $k_1 = 0$ thì tần suất từ không ảnh hưởng tới điểm, $k_1$ càng lớn thì tần suất càng có trọng lượng. Giá trị thường dùng nằm trong khoảng $[1{,}2; 2{,}0]$.
- $b \in [0, 1]$ điều khiển mức phạt tài liệu dài: $b = 1$ là chuẩn hóa độ dài đầy đủ, $b = 0$ là không chuẩn hóa. Giá trị thường dùng là $b = 0{,}75$.
- $IDF(q_i)$ (Inverse Document Frequency) đo lượng thông tin của từ $q_i$ trên toàn kho:

$$IDF(q_i) = \ln \frac{N - n(q_i) + 0{,}5}{n(q_i) + 0{,}5}$$

với $n(q_i)$ là số tài liệu chứa $q_i$. Từ xuất hiện ở hầu hết tài liệu (hư từ, từ thông dụng) có IDF thấp; thuật ngữ chuyên biệt có IDF cao. Đề tài dùng lớp `BM25Okapi` của thư viện `rank_bm25` với tham số mặc định $k_1 = 1{,}5$, $b = 0{,}75$; thư viện này thay các giá trị IDF âm (từ có mặt ở hơn nửa số tài liệu) bằng 0,25 lần IDF trung bình.

### 3.1.3 Ưu nhược điểm và vai trò trong hệ thống

- **Ưu điểm:** nhanh, chi phí tính toán thấp, không cần huấn luyện hay GPU, và khớp đúng các từ khóa chuyên biệt như số Điều, số Khoản hay thuật ngữ cố định (ví dụ `"Điều 357"`, `"bồi thường thiệt hại"`).
- **Hạn chế:** gặp vấn đề bất tương thích từ vựng (vocabulary mismatch). Khi người dùng hỏi bằng ngôn ngữ đời thường (ví dụ *"công ty nợ lương kéo dài"*) còn điều luật dùng từ ngữ pháp lý (*"không được trả lương đầy đủ hoặc trả lương không đúng thời hạn"*), hai bên ít từ chung nên BM25 khó nhận ra chúng liên quan.
- **Vai trò trong hệ thống:** BM25 là nhánh từ vựng của bộ truy xuất lai (mục 4.3), dùng công cụ tách từ tiếng Việt underthesea, để không bỏ sót các câu hỏi nêu số Điều hoặc thuật ngữ pháp lý cố định.

---

## 3.2 Truy xuất dày đặc (Dense Retrieval)

### 3.2.1 Khái niệm Dense Retrieval và kiến trúc Bi-encoder

Truy xuất dày đặc (dense retrieval) khắc phục vấn đề bất tương thích từ vựng bằng cách biểu diễn câu truy vấn và đoạn văn bản thành các vector nhúng (embedding) có số chiều cố định, thường từ 768 đến 1.024 chiều, trong cùng một không gian ngữ nghĩa.

Kiến trúc thường dùng là **bi-encoder** (Hình 3.1):
- Một bộ mã hóa (hoặc hai bộ dùng chung trọng số) mã hóa riêng câu truy vấn $Q$ và tài liệu $D$ thành hai vector $\vec{u} = \text{Encoder}(Q)$ và $\vec{v} = \text{Encoder}(D)$.
- Độ tương đồng giữa truy vấn và tài liệu được tính bằng tích vô hướng hoặc độ tương đồng cosine:

$$Sim(Q, D) = \cos(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}$$

Vì truy vấn và tài liệu được mã hóa riêng, toàn bộ kho văn bản có thể được mã hóa trước một lần và lưu thành chỉ mục vector. Khi có câu hỏi, hệ thống chỉ mã hóa câu hỏi rồi tìm các vector gần nhất bằng thuật toán tìm láng giềng gần đúng (Approximate Nearest Neighbor, ANN).

<!-- Hình 3.1: assets/diagrams/bi_encoder.png -->
**Hình 3.1.** Nguyên lý hoạt động của kiến trúc Bi-encoder trong Dense Retrieval.

### 3.2.2 Mô hình BGE-M3

Đề tài dùng mô hình nhúng **BGE-M3** (Chen và cộng sự, 2024), một mô hình mã nguồn mở hỗ trợ tiếng Việt. Chữ "M3" chỉ ba đặc tính:
1. **Multi-Linguality (đa ngôn ngữ):** hỗ trợ hơn 100 ngôn ngữ, trong đó có tiếng Việt.
2. **Multi-Functionality (đa chức năng):** cùng một mô hình sinh được vector dày (dense), trọng số từ vựng thưa (sparse) và biểu diễn đa vector kiểu ColBERT. Đề tài chỉ dùng vector dày 1.024 chiều.
3. **Multi-Granularity (đa độ dài):** xử lý được đầu vào tới 8.192 token. Đề tài giới hạn 2.048 token mỗi đoạn để giữ tốc độ khi chạy trên CPU (mục 4.3).

Chen và cộng sự (2024) huấn luyện mô hình bằng chưng cất tự tri thức (self-knowledge distillation): điểm kết hợp của ba cách biểu diễn được dùng làm tín hiệu dạy lại cho từng cách biểu diễn riêng lẻ.

### 3.2.3 Ưu nhược điểm và vai trò trong hệ thống

- **Ưu điểm:** tìm được điều luật liên quan tới câu hỏi tình huống đời thường ngay cả khi hai bên không có từ chung.
- **Hạn chế:** dễ nhầm các chi tiết định lượng hoặc số hiệu, chẳng hạn `"30 ngày"` với `"45 ngày"`, `"Điều 20"` với `"Điều 22"`, vì các đoạn chỉ khác nhau ở những chi tiết này có vector rất gần nhau. Chi phí tính toán và bộ nhớ cũng cao hơn BM25.
- **Vai trò trong hệ thống:** BGE-M3 là nhánh ngữ nghĩa của bộ truy xuất lai; vector được lưu trong ChromaDB (mục 4.3).

---

## 3.3 Kết hợp kết quả tìm kiếm: Reciprocal Rank Fusion (RRF)

### 3.3.1 Vấn đề bất đồng nhất điểm số giữa các hệ thống truy xuất

Khi kết hợp BM25 với dense retrieval, điểm của hai phương pháp không cùng thang đo:
- Điểm BM25 không có cận trên, phụ thuộc độ dài tài liệu, tần suất từ và kích thước kho.
- Độ tương đồng cosine của dense retrieval nằm trong đoạn $[-1, 1]$ và có phân phối khác hẳn.

Cộng điểm có trọng số $\alpha \cdot Score_{\text{BM25}} + (1 - \alpha) \cdot Score_{\text{Dense}}$ đòi hỏi chuẩn hóa điểm trước và phải chọn $\alpha$; một giá trị $\alpha$ hợp với tập câu hỏi này có thể không hợp với tập khác.

### 3.3.2 Thuật toán Reciprocal Rank Fusion (RRF)

Cormack và cộng sự (2009) đề xuất **Reciprocal Rank Fusion (RRF)**, chỉ dùng thứ hạng của tài liệu trong từng danh sách kết quả, không dùng điểm số.

Cho tập phương pháp truy xuất $M$ (trong đề tài, $M = \{\text{BM25}, \text{Dense}\}$), mỗi phương pháp $m \in M$ trả về danh sách tài liệu xếp theo độ liên quan giảm dần. Thứ hạng của tài liệu $d$ trong danh sách của $m$ ký hiệu là $r_m(d) \in \{1, 2, 3, \dots\}$. Điểm RRF của $d$ là:

$$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Trong đó:
- Tài liệu không có trong danh sách của phương pháp $m$ không được cộng điểm từ $m$.
- $k$ là hằng số làm giảm chênh lệch giữa các thứ hạng đầu (ví dụ hạng 1 và hạng 2), để một tài liệu xếp hạng cao ở cả hai danh sách được ưu tiên hơn tài liệu chỉ đứng đầu một danh sách. Cormack và cộng sự (2009) cố định $k = 60$ sau một thử nghiệm sơ bộ và dùng giá trị này cho mọi thực nghiệm; đề tài cũng dùng $k = 60$.

### 3.3.3 Vai trò trong hệ thống

Nguyen Ba và cộng sự (2024) cho thấy tìm kiếm lai bằng một biến thể chuẩn hóa của RRF đạt Recall cao hơn từng nhánh đơn lẻ trên dữ liệu pháp luật tiếng Việt. Trong đề tài, RRF hợp nhất 50 ứng viên từ mỗi nhánh BM25 và Dense, rồi 10 đoạn đứng đầu được đưa sang bước xếp hạng lại (mục 4.3).

---

## 3.4 Xếp hạng lại bằng Cross-Encoder: Mô hình BGE-Reranker-v2-M3

### 3.4.1 So sánh Bi-Encoder và Cross-Encoder

Bi-encoder tìm kiếm nhanh vì mã hóa truy vấn và tài liệu riêng rẽ, nhưng chính vì vậy hai chuỗi văn bản không tương tác với nhau ở cấp từ tố trong lúc mã hóa. Mô hình dễ bỏ qua các quan hệ phụ thuộc vào từng từ cụ thể, như phủ định hay điều kiện loại trừ, vốn thường gặp trong văn bản pháp luật.

**Cross-encoder** xử lý hạn chế này (Hình 3.2):
- Câu truy vấn $Q$ và đoạn ứng viên $D$ được ghép thành một chuỗi:
  $$\text{Input} = [CLS] \circ q_1 \dots q_n \circ [SEP] \circ d_1 \dots d_m \circ [SEP]$$
- Cả chuỗi đi qua các lớp self-attention của Transformer, nên ở mọi lớp, mỗi từ tố của câu hỏi đều được đối chiếu trực tiếp với từng từ tố của đoạn luật.
- Vector ẩn tại vị trí $[CLS]$ đi qua một lớp tuyến tính để ra một điểm liên quan $Score_{\text{Cross}}(Q, D)$.

<!-- Hình 3.2: assets/diagrams/cross_encoder.png -->
**Hình 3.2.** So sánh cơ chế tương tác giữa Bi-Encoder và Cross-Encoder.

Bảng 3.1 tóm tắt khác biệt giữa hai kiến trúc.

**Bảng 3.1.** So sánh đặc tính kỹ thuật giữa Bi-Encoder và Cross-Encoder.

| Đặc tính | Bi-Encoder (BGE-M3) | Cross-Encoder (BGE-Reranker-v2-M3) |
|---|---|---|
| **Cơ chế biểu diễn** | Mã hóa riêng $Q$ và $D$ | Mã hóa chung chuỗi $[Q; D]$ |
| **Tương tác từ tố** | Không có (chỉ so hai vector ở bước cuối) | Có, qua mọi lớp self-attention |
| **Mã hóa trước kho văn bản** | Có (tính một lần cho cả kho) | Không (phải tính lại cho từng cặp $Q, D$) |
| **Chi phí khi truy vấn** | Thấp: mã hóa câu hỏi, rồi tìm vector gần nhất | Cao: một lượt Transformer cho mỗi ứng viên |
| **Vai trò** | Lấy ứng viên trên toàn kho | Xếp hạng lại một số ít ứng viên, chính xác hơn |

### 3.4.2 Mô hình BGE-Reranker-v2-M3 và chiến lược hai tầng (Two-stage Retrieval)

Chạy cross-encoder trên toàn bộ hàng nghìn đoạn của kho luật cho mỗi câu hỏi là quá chậm, nhất là trên CPU. Cách làm phổ biến là **truy xuất hai tầng (two-stage retrieval)**:
1. **Tầng 1 (lấy ứng viên):** tìm kiếm lai BM25 + Dense kết hợp RRF thu hẹp kho xuống một tập ứng viên nhỏ ($K = 10$; với 20 ứng viên, bước xếp hạng lại mất khoảng 11 giây mỗi câu trên CPU, mục 4.3).
2. **Tầng 2 (xếp hạng lại):** cross-encoder `bge-reranker-v2-m3` chấm điểm lại 10 ứng viên và giữ 5 đoạn điểm cao nhất làm ngữ cảnh cho mô hình ngôn ngữ.

`bge-reranker-v2-m3` là mô hình xếp hạng lại đa ngôn ngữ thuộc cùng họ BGE với BGE-M3 và chạy được trên CPU. Đề tài giới hạn mỗi cặp (câu hỏi, đoạn) ở 512 token; ảnh hưởng của giới hạn này được nêu ở mục 5.7.

---

## 3.5 Kỹ thuật Retrieval-Augmented Generation (RAG)

### 3.5.1 Khái niệm và kiến trúc RAG kinh điển

Mô hình ngôn ngữ lớn (LLM) chỉ biết những gì có trong dữ liệu huấn luyện, được lưu trong tham số của mô hình (parametric memory), và có thể sinh ra thông tin sai nhưng diễn đạt trôi chảy, gọi là ảo giác (hallucination). Trong tư vấn pháp lý, một căn cứ bịa ra có thể khiến người hỏi hiểu sai quyền và nghĩa vụ của mình.

**Retrieval-Augmented Generation (RAG)**, do Lewis và cộng sự (2020) đề xuất, kết hợp tri thức trong tham số của LLM với một kho tri thức bên ngoài (non-parametric memory). Kiến trúc RAG gồm hai phần:
1. **Bộ truy xuất (retriever):** nhận câu hỏi $Q$, tìm trong kho tri thức và trả về $k$ đoạn ngữ cảnh liên quan $C = \{c_1, c_2, \dots, c_k\}$.
2. **Bộ sinh (generator):** nhận câu hỏi cùng ngữ cảnh và sinh câu trả lời $A$ theo xác suất có điều kiện:

$$P(A | Q, C) = \prod_{t=1}^{T} P(a_t | a_{<t}, Q, C)$$

Hình 3.3 minh họa luồng một lượt này: kho văn bản được lập chỉ mục từ trước, mỗi câu hỏi được truy xuất một lần rồi sinh câu trả lời.

<!-- Hình 3.3: assets/diagrams/naive_rag.png -->
**Hình 3.3.** Quy trình tuyến tính một lượt của hệ thống RAG truyền thống (Naive RAG).

### 3.5.2 Hạn chế của RAG truyền thống trong bài toán pháp luật

RAG một lượt (naive RAG) giảm được ảo giác nhưng còn một số hạn chế khi áp dụng cho pháp luật:
- **Không tự kiểm tra bằng chứng:** nếu bước truy xuất trả về điều luật không liên quan hoặc chỉ liên quan một phần, bộ sinh vẫn phải trả lời dựa trên ngữ cảnh đó, dẫn tới câu trả lời sai hoặc lạc đề.
- **Không nhận ra câu hỏi ngoài phạm vi:** hệ thống không phân biệt được câu hỏi nằm ngoài kho văn bản hoặc không có căn cứ tương ứng, nên vẫn cố trả lời thay vì từ chối.
- **Trích dẫn không hỗ trợ (unsupported citations):** khi xây dựng bộ đánh giá ALCE, Gao và cộng sự (2023) nhận thấy ngay cả các mô hình tốt nhất khi đó vẫn có nhiều câu trả lời mà trích dẫn không hỗ trợ đầy đủ nội dung được khẳng định.
- **Không thích ứng theo loại câu hỏi:** câu hỏi nêu đích danh số Điều cần lấy đúng Điều đó, còn câu hỏi tình huống phức tạp có thể cần viết lại truy vấn và truy xuất thêm; một luồng cố định không đáp ứng được cả hai.

---

## 3.6 Kiến trúc Agentic-RAG

### 3.6.1 Từ RAG thụ động đến Tác tử Agentic-RAG

Để khắc phục các hạn chế trên, nhiều nghiên cứu gần đây để mô hình ngôn ngữ tự quyết định có cần truy xuất thêm và tự đánh giá kết quả trung gian (Asai và cộng sự, 2024; Yan và cộng sự, 2024); trong lĩnh vực pháp luật Việt Nam, Pham và cộng sự (2025) xây dựng một trợ lý tư vấn theo hướng Agentic-RAG. Cách tiếp cận này gọi chung là **Agentic-RAG** (Hình 3.4). Tác tử (agent) ở đây là một chương trình có khả năng:
- **Theo dõi trạng thái:** ghi nhớ các truy vấn đã thử, bằng chứng đã có và chất lượng của bằng chứng đó.
- **Dùng công cụ:** tự chọn công cụ phù hợp, như tra cứu thẳng một Điều hay tìm kiếm lai có lọc theo thời gian.
- **Tự đánh giá:** kiểm tra kết quả trung gian, phát hiện chỗ thiếu và thực hiện bước khắc phục trước khi trả lời.

<!-- Hình 3.4: assets/diagrams/agentic_rag.png -->
**Hình 3.4.** Luồng điều phối của Agentic-RAG so với RAG truyền thống.

### 3.6.2 Các cơ chế thành phần trong hệ thống Agentic-RAG

Tác tử của đề tài gồm ba cơ chế sau.

#### 1. Định tuyến câu hỏi (Query Routing)
Trước khi truy xuất, tác tử phân loại câu hỏi:
- *Tra cứu trực tiếp (direct):* người dùng nêu tên văn bản và số Điều (ví dụ *"Điều 20 Bộ luật Lao động 2019 quy định gì?"*). Tác tử lấy thẳng toàn văn Điều đó, không qua tìm kiếm; nếu không có Điều đó thì quay về truy xuất thường.
- *Câu hỏi tình huống (situational):* cần tìm căn cứ cho một tình huống thực tế. Tác tử đồng thời trích ngày xảy ra sự việc (nếu có) để lọc văn bản theo hiệu lực.
- *Câu hỏi ngoài phạm vi (out-of-scope):* không phải câu hỏi pháp luật, hoặc hỏi về vấn đề mà 5 văn bản trong kho không điều chỉnh (ví dụ tội phạm và hình phạt, xử phạt hành chính, thủ tục hành chính, thuế). Tác tử từ chối ngay, không tốn lượt truy xuất và sinh câu trả lời.

#### 2. Tự đánh giá bằng chứng và viết lại truy vấn (Self-Grading & Query Rewriting)
Bước này dựa trên ý tưởng tự đánh giá bằng chứng của Corrective RAG (Yan và cộng sự, 2024) và Self-RAG (Asai và cộng sự, 2024), đã trình bày ở mục 2.3, và được hiện thực bằng một prompt có đầu ra JSON trên đồ thị trạng thái.

Sau khi truy xuất, nút đánh giá (grade) kiểm tra các đoạn luật thu được đã đủ để trả lời câu hỏi chưa. Nếu chưa đủ, mô hình đề xuất một truy vấn mới và tác tử truy xuất thêm, tối đa 2 lần viết lại; hết lượt mà vẫn chưa đủ thì tác tử từ chối vì căn cứ không đủ.

#### 3. Kiểm chứng trích dẫn hai lớp (Two-tier Citation Verification)
Câu trả lời gắn mã đoạn luật sau mỗi câu, và được kiểm chứng qua hai lớp:
1. **Lớp (a), kiểm tra cú pháp (không gọi LLM):** dùng biểu thức chính quy tìm mọi mã trích dẫn trong câu trả lời (dạng `[BLLD2019_Dieu20_Khoan1]`), chuẩn hóa về đúng dạng trong kho rồi đối chiếu với các đoạn đã đưa vào ngữ cảnh. Mã nào trỏ tới đoạn không có trong ngữ cảnh bị gỡ, nên hệ thống không trả về trích dẫn tới đoạn mà mô hình chưa đọc.
2. **Lớp (b), kiểm tra ngữ nghĩa (1 lượt LLM):** mô hình xét từng cặp (câu khẳng định, đoạn được trích) và chỉ ra cặp nào đoạn luật không hỗ trợ nội dung câu; các mã đó bị gỡ.

Câu nào mất hết trích dẫn sau hai lớp thì câu trả lời được sinh lại một lần; nếu vẫn còn câu như vậy, câu đó được giữ nhưng gắn nhãn "(chưa có căn cứ)". Hiệu quả của cơ chế này được đo ở mục 5.4.3 (phép thử tiêm trích dẫn sai) và mục 5.6 (phân tích lỗi).

---

## 3.7 Đồ thị trạng thái LangGraph

### 3.7.1 Hạn chế của các framework chuỗi tuyến tính (Linear Chains)

Trong các thư viện xây dựng ứng dụng LLM thế hệ đầu (như các chuỗi của LangChain), luồng thực thi là một chuỗi các bước nối tiếp, không có vòng lặp, ví dụ `Prompt -> LLM -> OutputParser`. Cách tổ chức này hợp với xử lý một chiều.

Một tác tử Agentic-RAG như ở mục 3.6 lại cần:
- Vòng lặp có điều kiện, để truy xuất lại khi bằng chứng chưa đủ.
- Rẽ nhánh theo quyết định của bước định tuyến.
- Một trạng thái chung được cập nhật qua các bước.

### 3.7.2 Nguyên lý hoạt động của LangGraph

LangGraph là thư viện trong hệ sinh thái LangChain, dùng để xây dựng tác tử dưới dạng **đồ thị trạng thái có chu trình (cyclic state graph)**.

LangGraph gồm ba thành phần:
1. **Trạng thái (State):** một cấu trúc dữ liệu (thường khai báo bằng `typing.TypedDict`) đóng vai trò bộ nhớ chung của tác tử. Mỗi nút đọc trạng thái và trả về phần cần cập nhật.
   - Trong đề tài, trạng thái chứa câu hỏi, loại câu hỏi, ngày sự việc, các truy vấn đã dùng, bằng chứng đã truy xuất, số lần viết lại, câu trả lời, trích dẫn và dấu vết thực thi.
2. **Nút (Node):** mỗi nút là một hàm nhận trạng thái và trả về phần cập nhật. Tác tử của đề tài có 7 nút: `route`, `lookup_article`, `retrieve`, `grade`, `generate`, `verify`, `refuse`.
3. **Cạnh (Edge) và cạnh có điều kiện (Conditional Edge):**
   - *Cạnh cố định:* nối thẳng tới một nút xác định (ví dụ `refuse` luôn đi tới kết thúc).
   - *Cạnh có điều kiện:* một hàm nhận trạng thái và trả về tên nút tiếp theo. Ví dụ sau nút `grade`: đủ bằng chứng thì sang `generate`; chưa đủ và còn lượt viết lại thì quay về `retrieve`; hết lượt thì sang `refuse` để từ chối vì căn cứ không đủ.

Đồ thị cụ thể của tác tử trong đề tài được trình bày ở Hình 4.2 (mục 4.4.1).

### 3.7.3 Vai trò trong hệ thống

Mỗi nút là một hàm riêng nên kiểm thử được độc lập, và mỗi bước được ghi vào dấu vết thực thi (mục 4.4.4). Các thành phần router, grade và verify (b) bật, tắt được bằng cờ cấu hình trên cùng một đồ thị, phục vụ nghiên cứu lược bỏ của RQ3 (mục 4.4.3, 5.4).

---

## 3.8 Đặc thù văn bản quy phạm pháp luật Việt Nam

### 3.8.1 Cấu trúc phân cấp hình thức và hiện tượng Document-Level Retrieval Mismatch (DRM)

Văn bản luật Việt Nam được trình bày theo cấu trúc phân cấp:
$$\text{Văn bản} \longrightarrow \text{Phần} \longrightarrow \text{Chương} \longrightarrow \text{Mục} \longrightarrow \text{Điều} \longrightarrow \text{Khoản} \longrightarrow \text{Điểm}$$

Một quy định trọn vẹn thường nằm trong một **Khoản** hoặc một **Điều**. Nếu cắt văn bản thành các đoạn có độ dài cố định, như cách thường làm trong các ứng dụng RAG (ví dụ cửa sổ 200 từ chồng lấp 40 từ, biến thể đối chứng ở RQ2), sẽ có hai vấn đề:
1. **Quy định bị cắt đôi:** điều kiện áp dụng ở đầu Điều có thể nằm ở đoạn khác với hệ quả pháp lý ở cuối Điều, khiến mô hình ngôn ngữ hiểu sai quy định.
2. **Mất ngữ cảnh nguồn và hiện tượng DRM:** Reuter và cộng sự (2025) chỉ ra rằng trong kho văn bản pháp luật lớn, nhiều điều khoản thuộc các văn bản khác nhau có tiêu đề và cách diễn đạt giống nhau (ví dụ về thời giờ làm việc, hợp đồng vô hiệu, quyền của người lao động). Đoạn văn tách khỏi tên văn bản và tên Điều dễ bị truy xuất nhầm sang một văn bản khác cùng chủ đề; hiện tượng này gọi là **Document-Level Retrieval Mismatch (DRM)**.

Reuter và cộng sự (2025) giảm DRM bằng cách gắn bản tóm tắt văn bản vào từng đoạn. Đề tài áp dụng ý tưởng này ở dạng gọn hơn: văn bản đem đi nhúng của mỗi đoạn được gắn thêm một dòng tiêu đề phân cấp:
$$\text{Tiêu đề} = \text{[Tên văn bản]} - \text{[Điều X]} - \text{[Tên Điều]} - \text{[Khoản Y]}$$
để đoạn ngắn không mất ngữ cảnh nguồn. Hiệu quả của cách gắn tiêu đề được đo ở RQ2 (mục 5.3).

### 3.8.2 Hiệu lực pháp luật theo thời gian (Temporal Validity)

Nguyên tắc chung khi áp dụng pháp luật là: **sự việc xảy ra vào thời điểm nào thì áp dụng văn bản quy phạm pháp luật có hiệu lực tại thời điểm đó**, trừ trường hợp văn bản có quy định hiệu lực trở về trước.

Kho văn bản pháp luật thay đổi theo thời gian:
- Luật mới thay thế luật cũ: Bộ luật Lao động 2019 có hiệu lực từ 01/01/2021 và thay thế Bộ luật Lao động 2012.
- Nhiều quy định cụ thể thay đổi về quyền và nghĩa vụ. Chẳng hạn:
  - *Bộ luật Lao động 2012 (Điều 22):* có ba loại hợp đồng lao động, trong đó có hợp đồng theo mùa vụ hoặc theo một công việc nhất định có thời hạn dưới 12 tháng.
  - *Bộ luật Lao động 2019 (Điều 20):* chỉ còn hai loại hợp đồng, xác định thời hạn và không xác định thời hạn.
  - *Quyền đơn phương chấm dứt hợp đồng của người lao động:* theo Bộ luật Lao động 2012 (Điều 37), người làm hợp đồng xác định thời hạn phải có một trong các lý do luật định; theo Bộ luật Lao động 2019 (Điều 35), người lao động chỉ cần báo trước đủ thời hạn.

Nếu người dùng hỏi *"Năm 2019, tôi ký hợp đồng lao động theo mùa vụ thì thời hạn tối đa là bao lâu?"*, một hệ thống chỉ có văn bản hiện hành (Bộ luật Lao động 2019) sẽ trả lời rằng luật không còn hợp đồng mùa vụ, sai với sự việc đã xảy ra năm 2019.

Để xử lý, mỗi văn bản $L$ trong kho được gán khoảng hiệu lực $[d_{\text{effective}}, d_{\text{expiry}})$; văn bản còn hiệu lực có $d_{\text{expiry}}$ để trống. Với câu hỏi có ngày sự việc $d_{\text{event}}$, văn bản được dùng khi:

$$d_{\text{effective}} \le d_{\text{event}} < d_{\text{expiry}}$$

Với chính sách lọc theo ngày sự việc, chỉ văn bản thỏa điều kiện trên mới được đưa vào tìm kiếm; hai chính sách đối chứng được nêu ở mục 4.3. Đây là cơ sở để thiết kế bộ lọc theo siêu dữ liệu và tập câu hỏi có mốc thời gian cho RQ4 (mục 4.3, 5.5).

---

## 3.9 Tóm tắt chương

Chương 3 đã trình bày cơ sở lý thuyết của các kỹ thuật dùng trong hệ thống:
1. **Truy xuất lai:** BM25 khớp từ khóa chính xác, BGE-M3 nắm ngữ nghĩa, hai danh sách được hợp nhất bằng RRF rồi xếp hạng lại bằng cross-encoder BGE-Reranker-v2-M3.
2. **Agentic-RAG:** khắc phục hạn chế của RAG một lượt bằng định tuyến câu hỏi, tự đánh giá bằng chứng và viết lại truy vấn, cùng kiểm chứng trích dẫn hai lớp.
3. **LangGraph:** biểu diễn tác tử bằng đồ thị trạng thái có chu trình, cho phép bật, tắt từng thành phần để làm nghiên cứu lược bỏ.
4. **Đặc thù pháp luật Việt Nam:** phân đoạn theo cấu trúc Điều, Khoản kèm tiêu đề phân cấp để giảm truy xuất nhầm văn bản, và lọc văn bản theo khoảng hiệu lực tại thời điểm sự việc.

Chương 4 trình bày thiết kế và cài đặt hệ thống dựa trên các cơ sở này.
