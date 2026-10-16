# Zalo AI Legal Text Retrieval 2021 (tập con)

Nguồn: https://huggingface.co/datasets/GreenNode/zalo-ai-legal-text-retrieval-vn (giấy phép MIT), tải ngày 2026-10-15.
Chỉ giữ `queries.jsonl` và `qrels/{train,test}.jsonl`; corpus không cần vì căn cứ đã có dạng `<số hiệu>+<số Điều>`.
`python -m eval.import_cases` lọc các câu có mọi căn cứ thuộc kho (BLDS 2015, LDN 2020).
