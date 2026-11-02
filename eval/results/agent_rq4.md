| run | source | n | Trả lời | Citation P | Citation R | Từ chối đúng | Đúng phiên bản | Faithfulness | Correctness | LLM/câu | ms/câu |
|---|---|---|---|---|---|---|---|---|---|---|---|
| full@any | all | 12 | 0.917 | 0.803 | 0.833 | 0.917 | 0.667 | 0.909 | 0.833 | 5.000 | 17281.750 |
| full@any | manual | 12 | 0.917 | 0.803 | 0.833 | 0.917 | 0.667 | 0.909 | 0.833 | 5.000 | 17281.750 |
| full@current | all | 12 | 0.667 | 0.542 | 0.417 | 0.667 | 0.417 | 1.000 | 0.583 | 4.167 | 18154.583 |
| full@current | manual | 12 | 0.667 | 0.542 | 0.417 | 0.667 | 0.417 | 1.000 | 0.583 | 4.167 | 18154.583 |
| full@event | all | 12 | 0.917 | 0.788 | 0.833 | 0.917 | 0.833 | 1.000 | 0.833 | 4.333 | 11837.750 |
| full@event | manual | 12 | 0.917 | 0.788 | 0.833 | 0.917 | 0.833 | 1.000 | 0.833 | 4.333 | 11837.750 |

Cách đọc: mỗi chỉ số là trung bình trên các câu áp dụng được (bỏ giá trị trống): Citation P chỉ tính câu có trích dẫn; Faithfulness chỉ tính câu được trả lời; Correctness chỉ tính câu có đáp án mẫu (không có câu Zalo). Đọc kèm cột "Trả lời". Cột ms có cache LLM, không dùng để so latency (đo riêng bằng `run --cache-dir <thư mục mới>`).

Chênh lệch so với `full@event` (ghép cặp theo câu, bootstrap 95%; * = khoảng không chứa 0; n = số câu của cột Recall):

| run | n | answered | precision | recall | refusal_ok | version_ok | correctness |
|---|---|---|---|---|---|---|---|
| full@any | 12 | 0.000 [-0.250; 0.250] | 0.017 [-0.100; 0.150] (n=10) | 0.000 [-0.333; 0.333] | 0.000 [-0.250; 0.250] | -0.167 [-0.500; 0.167] | 0.000 [-0.250; 0.250] |
| full@current | 12 | -0.250 [-0.500; 0.000] | -0.167 [-0.417; 0.000] (n=8) | -0.417* [-0.667; -0.167] | -0.250 [-0.500; 0.000] | -0.417* [-0.667; -0.167] | -0.250 [-0.500; 0.000] |
