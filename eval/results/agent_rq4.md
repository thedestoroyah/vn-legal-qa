| run | source | n | Trả lời | Citation P | Citation R | Từ chối đúng | Đúng phiên bản | Faithfulness | Correctness | LLM/câu | ms/câu |
|---|---|---|---|---|---|---|---|---|---|---|---|
| full@any | all | 32 | 0.875 | 0.764 | 0.625 | 0.875 | 0.562 | 0.857 | 0.703 | 4.875 | 64041.438 |
| full@any | manual | 32 | 0.875 | 0.764 | 0.625 | 0.875 | 0.562 | 0.857 | 0.703 | 4.875 | 64041.438 |
| full@current | all | 32 | 0.719 | 0.606 | 0.469 | 0.719 | 0.438 | 1.000 | 0.578 | 4.125 | 24268.031 |
| full@current | manual | 32 | 0.719 | 0.606 | 0.469 | 0.719 | 0.438 | 1.000 | 0.578 | 4.125 | 24268.031 |
| full@event | all | 32 | 0.781 | 0.907 | 0.781 | 0.781 | 0.750 | 1.000 | 0.766 | 4.094 | 11854.719 |
| full@event | manual | 32 | 0.781 | 0.907 | 0.781 | 0.781 | 0.750 | 1.000 | 0.766 | 4.094 | 11854.719 |

Cách đọc: mỗi chỉ số là trung bình trên các câu áp dụng được (bỏ giá trị trống): Citation P chỉ tính câu có trích dẫn; Faithfulness chỉ tính câu được trả lời; Correctness chỉ tính câu có đáp án mẫu (không có câu Zalo). Đọc kèm cột "Trả lời". Cột ms có cache LLM, không dùng để so latency (đo riêng bằng `run --cache-dir <thư mục mới>`).

Chênh lệch so với `full@event` (ghép cặp theo câu, bootstrap 95%; * = khoảng không chứa 0; n = số câu của cột Recall):

| run | n | answered | precision | recall | refusal_ok | version_ok | correctness |
|---|---|---|---|---|---|---|---|
| full@any | 32 | 0.094 [-0.062; 0.250] | -0.042 [-0.183; 0.075] (n=20) | -0.156 [-0.344; 0.031] | 0.094 [-0.062; 0.250] | -0.188 [-0.375; 0.000] | -0.062 [-0.219; 0.094] |
| full@current | 32 | -0.062 [-0.250; 0.125] | -0.175* [-0.333; -0.035] (n=19) | -0.312* [-0.500; -0.156] | -0.062 [-0.250; 0.125] | -0.312* [-0.500; -0.156] | -0.188* [-0.344; -0.062] |
