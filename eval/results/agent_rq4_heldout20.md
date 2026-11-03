| run | source | n | Trả lời | Citation P | Citation R | Từ chối đúng | Đúng phiên bản | Faithfulness | Correctness | LLM/câu | ms/câu |
|---|---|---|---|---|---|---|---|---|---|---|---|
| full@any | all | 20 | 0.850 | 0.692 | 0.500 | 0.850 | 0.450 | 0.824 | 0.575 | 4.700 | 91314.850 |
| full@any | manual | 20 | 0.850 | 0.692 | 0.500 | 0.850 | 0.450 | 0.824 | 0.575 | 4.700 | 91314.850 |
| full@current | all | 20 | 0.750 | 0.607 | 0.450 | 0.750 | 0.450 | 1.000 | 0.525 | 4.050 | 28617.300 |
| full@current | manual | 20 | 0.750 | 0.607 | 0.450 | 0.750 | 0.450 | 1.000 | 0.525 | 4.050 | 28617.300 |
| full@event | all | 20 | 0.700 | 0.964 | 0.700 | 0.700 | 0.700 | 1.000 | 0.675 | 3.900 | 12521.400 |
| full@event | manual | 20 | 0.700 | 0.964 | 0.700 | 0.700 | 0.700 | 1.000 | 0.675 | 3.900 | 12521.400 |

Cách đọc: mỗi chỉ số là trung bình trên các câu áp dụng được (bỏ giá trị trống): Citation P chỉ tính câu có trích dẫn; Faithfulness chỉ tính câu được trả lời; Correctness chỉ tính câu có đáp án mẫu (không có câu Zalo). Đọc kèm cột "Trả lời". Cột ms có cache LLM, không dùng để so latency (đo riêng bằng `run --cache-dir <thư mục mới>`).

Chênh lệch so với `full@event` (ghép cặp theo câu, bootstrap 95%; * = khoảng không chứa 0; n = số câu của cột Recall):

| run | n | answered | precision | recall | refusal_ok | version_ok | correctness |
|---|---|---|---|---|---|---|---|
| full@any | 20 | 0.150 [-0.050; 0.350] | -0.100 [-0.350; 0.100] (n=10) | -0.200 [-0.400; 0.000] | 0.150 [-0.050; 0.350] | -0.250 [-0.500; 0.000] | -0.100 [-0.300; 0.100] |
| full@current | 20 | 0.050 [-0.150; 0.250] | -0.182 [-0.455; 0.000] (n=11) | -0.250* [-0.450; -0.050] | 0.050 [-0.150; 0.250] | -0.250* [-0.450; -0.050] | -0.150 [-0.300; 0.000] |
