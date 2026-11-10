## Lời cảm ơn

Chúng em xin gửi lời cảm ơn tới thầy Lê Anh Cường đã tận tình giảng dạy, giúp đỡ và hướng dẫn chúng em hoàn thành báo cáo này. Trong quá trình thực hiện, nhóm em đã nhận được nhiều ý kiến đóng góp từ thầy, giúp nhóm em hiểu rõ hơn về các vấn đề phức tạp trong môn học và có được cái nhìn tổng quát hơn về những kiến thức liên quan đến đề tài.

Cuối cùng, nhóm em xin chân thành cảm ơn thầy đã đồng hành và hỗ trợ trong quá trình học tập và nghiên cứu. Dù đã cố gắng thực hiện đề tài một cách hoàn chỉnh nhất, song vì hạn chế về kiến thức và thời gian nên vẫn còn nhiều thiếu sót, chúng em rất mong được sự đóng góp ý kiến của thầy để bài báo cáo được hoàn thiện hơn.

## Tóm tắt

Mô hình ngôn ngữ lớn có thể trả lời câu hỏi pháp luật nhưng dễ trích sai căn cứ hoặc dùng văn bản không có hiệu lực vào thời điểm xảy ra sự việc. Đề tài xây dựng hệ thống hỏi đáp pháp luật tiếng Việt theo hướng Agentic-RAG trên 5 văn bản luật: Bộ luật Dân sự 2015, Bộ luật Lao động 2012 và 2019, Luật Doanh nghiệp 2020, Luật Thương mại 2005. Văn bản được tách thành Điều, Khoản kèm khoảng hiệu lực; bộ truy xuất kết hợp BM25 với tìm kiếm ngữ nghĩa bằng RRF, xếp hạng lại bằng cross-encoder và lọc văn bản theo ngày sự việc. Tác tử LangGraph định tuyến câu hỏi, đánh giá bằng chứng, sinh câu trả lời có trích dẫn tới Khoản và kiểm chứng trích dẫn hai lớp.

Hệ thống được đánh giá trên 209 câu hỏi, trong đó có tập giữ riêng 30 câu soạn sau khi đã cố định prompt. Truy xuất lai kèm xếp hạng lại đạt Hit@5 0,844 và Recall@10 0,872 trên 77 câu của bộ Zalo; tác tử đầy đủ đạt Citation Precision 0,870. So với RAG một lượt, tỷ lệ trích đúng phiên bản luật cao hơn 0,250; lọc theo ngày sự việc cao hơn 0,312 về đúng phiên bản so với chỉ dùng văn bản còn hiệu lực, trên 32 câu có mốc thời gian. Hạn chế chính là prompt được chỉnh trên tập kiểm thử, bộ chấm tự động chưa được kiểm định đủ và cỡ mẫu còn nhỏ.

## Abstract

Large language models can answer legal questions, but they often cite the wrong provision or rely on a law that was not in force when the event happened. This project builds a Vietnamese legal question answering system based on Agentic-RAG over five statutes: the Civil Code 2015, the Labour Code 2012 and 2019, the Law on Enterprises 2020 and the Commercial Law 2005. The statutes are split into articles and clauses annotated with their validity periods; retrieval combines BM25 and dense search with Reciprocal Rank Fusion, reranks the candidates with a cross-encoder and keeps only documents in force on the date of the event. A LangGraph agent routes the question, grades the evidence, generates an answer that cites specific clauses and verifies its citations in two layers.

The system is evaluated on 209 questions, including a held-out set of 30 questions written after the prompts were frozen. Hybrid retrieval with reranking reaches a Hit@5 of 0.844 and a Recall@10 of 0.872 on 77 Zalo questions, and the full agent reaches a Citation Precision of 0.870. Compared with single-pass RAG, the rate of citing the correct version of the law is 0.250 higher; filtering by event date beats using only laws currently in force by 0.312 on version correctness over 32 time-dependent questions. The main limitations are prompt tuning on the test set, weak validation of the automatic judge and small sample sizes.

## Viết tắt

|   |   |
|---|---|
| AI | Artificial Intelligence (trí tuệ nhân tạo) |
| ALCE | Automatic LLMs' Citation Evaluation |
| ALQAC | Automated Legal Question Answering Competition |
| ANN | Approximate Nearest Neighbor (tìm láng giềng gần đúng) |
| API | Application Programming Interface |
| BGE-M3 | BAAI General Embedding M3 (Multi-Linguality, Multi-Functionality, Multi-Granularity) |
| BLDS | Bộ luật Dân sự |
| BLLĐ | Bộ luật Lao động |
| BM25 | Best Matching 25 |
| CPU | Central Processing Unit |
| DRM | Document-Level Retrieval Mismatch (truy xuất nhầm văn bản) |
| GPU | Graphics Processing Unit |
| IDF | Inverse Document Frequency |
| JSON | JavaScript Object Notation |
| JSONL | JSON Lines (mỗi dòng một đối tượng JSON) |
| LLM | Large Language Model (mô hình ngôn ngữ lớn) |
| MRR | Mean Reciprocal Rank |
| RAG | Retrieval-Augmented Generation |
| RAGAS | Retrieval Augmented Generation Assessment |
| RQ | Research Question (câu hỏi nghiên cứu) |
| RRF | Reciprocal Rank Fusion |
| TF-IDF | Term Frequency – Inverse Document Frequency |
| VLQA | Vietnamese Legal Question Answering |
