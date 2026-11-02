| run | source | n | Trả lời | Citation P | Citation R | Từ chối đúng | Đúng phiên bản | Faithfulness | Correctness | LLM/câu | ms/câu |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | all | 179 | 0.883 | 0.820 | 0.835 | 0.911 | 0.500 | 0.994 | 0.863 | 1.000 | 31749.821 |
| baseline | manual | 37 | 0.784 | 0.793 | 0.750 | 0.919 | 0.500 | 0.983 | 0.784 | 1.000 | 64659.054 |
| baseline | synthetic | 65 | 0.985 | 0.880 | 0.969 | 0.985 | – | 1.000 | 0.908 | 1.000 | 22626.123 |
| baseline | zalo | 77 | 0.844 | 0.774 | 0.758 | 0.844 | – | 0.992 | – | 1.000 | 23638.117 |
| full | all | 179 | 0.888 | 0.850 | 0.830 | 0.916 | 0.833 | 0.991 | 0.897 | 4.039 | 16606.587 |
| full | manual | 37 | 0.838 | 0.889 | 0.906 | 0.973 | 0.833 | 1.000 | 0.932 | 3.676 | 12316.703 |
| full | synthetic | 65 | 0.923 | 0.912 | 0.877 | 0.923 | – | 0.983 | 0.877 | 4.108 | 12658.600 |
| full | zalo | 77 | 0.883 | 0.780 | 0.758 | 0.883 | – | 0.993 | – | 4.156 | 22000.675 |

Cách đọc: mỗi chỉ số là trung bình trên các câu áp dụng được (bỏ giá trị trống): Citation P chỉ tính câu có trích dẫn; Faithfulness chỉ tính câu được trả lời; Correctness chỉ tính câu có đáp án mẫu (không có câu Zalo). Đọc kèm cột "Trả lời". Cột ms có cache LLM, không dùng để so latency (đo riêng bằng `run --cache-dir <thư mục mới>`).

Chênh lệch so với `full` (ghép cặp theo câu, bootstrap 95%; * = khoảng không chứa 0; n = số câu của cột Recall):

| run | n | answered | precision | recall | refusal_ok | version_ok | correctness |
|---|---|---|---|---|---|---|---|
| baseline | 174 | -0.006 [-0.050; 0.039] (n=179) | -0.035* [-0.068; -0.006] (n=144) | 0.006 [-0.057; 0.069] | -0.006 [-0.050; 0.039] (n=179) | -0.333 [-0.667; 0.000] (n=12) | -0.034 [-0.093; 0.020] (n=102) |
