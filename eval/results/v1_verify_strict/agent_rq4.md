| run | source | n | Trả lời | Citation P | Citation R | Từ chối đúng | Đúng phiên bản | Faithfulness | Correctness | LLM/câu | ms/câu |
|---|---|---|---|---|---|---|---|---|---|---|---|
| full@any | all | 12 | 0.917 | 0.812 | 0.583 | 0.917 | 0.500 | 0.909 | 0.833 | 5.333 | 15447.583 |
| full@any | manual | 12 | 0.917 | 0.812 | 0.583 | 0.917 | 0.500 | 0.909 | 0.833 | 5.333 | 15447.583 |
| full@current | all | 12 | 0.667 | 0.571 | 0.333 | 0.667 | 0.417 | 1.000 | 0.583 | 4.500 | 19355.250 |
| full@current | manual | 12 | 0.667 | 0.571 | 0.333 | 0.667 | 0.417 | 1.000 | 0.583 | 4.500 | 19355.250 |
| full@event | all | 12 | 0.917 | 0.792 | 0.583 | 0.917 | 0.667 | 1.000 | 0.833 | 4.833 | 15911.917 |
| full@event | manual | 12 | 0.917 | 0.792 | 0.583 | 0.917 | 0.667 | 1.000 | 0.833 | 4.833 | 15911.917 |

Cách đọc: mỗi chỉ số là trung bình trên các câu áp dụng được (bỏ giá trị trống): Citation P chỉ tính câu có trích dẫn; Faithfulness chỉ tính câu được trả lời; Correctness chỉ tính câu có đáp án mẫu (không có câu Zalo). Đọc kèm cột "Trả lời". Cột ms có cache LLM, không dùng để so latency (đo riêng bằng `run --cache-dir <thư mục mới>`).
