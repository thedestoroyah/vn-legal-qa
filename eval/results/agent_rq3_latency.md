| run | source | n | Trả lời | Citation P | Citation R | Từ chối đúng | Đúng phiên bản | Faithfulness | Correctness | LLM/câu | ms/câu |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | all | 19 | 1.000 | 0.868 | 0.947 | 1.000 | 0.667 | – | – | 1.000 | 8108.316 |
| baseline | manual | 6 | 1.000 | 0.750 | 0.833 | 1.000 | 0.667 | – | – | 1.000 | 10584.667 |
| baseline | synthetic | 6 | 1.000 | 0.917 | 1.000 | 1.000 | – | – | – | 1.000 | 6701.500 |
| baseline | zalo | 7 | 1.000 | 0.929 | 1.000 | 1.000 | – | – | – | 1.000 | 7191.571 |
| full | all | 19 | 0.947 | 0.912 | 0.895 | 0.947 | 1.000 | – | – | 3.895 | 16174.526 |
| full | manual | 6 | 1.000 | 0.900 | 0.833 | 1.000 | 1.000 | – | – | 4.333 | 15550.000 |
| full | synthetic | 6 | 1.000 | 0.917 | 1.000 | 1.000 | – | – | – | 3.833 | 15489.667 |
| full | zalo | 7 | 0.857 | 0.917 | 0.857 | 0.857 | – | – | – | 3.571 | 17296.857 |
| no_grading | all | 19 | 0.947 | 0.912 | 0.895 | 0.947 | 1.000 | – | – | 3.000 | 10885.474 |
| no_grading | manual | 6 | 1.000 | 0.900 | 0.833 | 1.000 | 1.000 | – | – | 3.333 | 14119.500 |
| no_grading | synthetic | 6 | 1.000 | 0.917 | 1.000 | 1.000 | – | – | – | 3.000 | 11613.000 |
| no_grading | zalo | 7 | 0.857 | 0.917 | 0.857 | 0.857 | – | – | – | 2.714 | 7489.857 |
| no_router | all | 19 | 1.000 | 0.861 | 0.895 | 1.000 | 0.667 | – | – | 3.316 | 22449.579 |
| no_router | manual | 6 | 1.000 | 0.700 | 0.667 | 1.000 | 0.667 | – | – | 3.833 | 26833.833 |
| no_router | synthetic | 6 | 1.000 | 0.917 | 1.000 | 1.000 | – | – | – | 3.167 | 26965.833 |
| no_router | zalo | 7 | 1.000 | 0.929 | 1.000 | 1.000 | – | – | – | 3.000 | 14820.571 |
| no_verify | all | 18 | 0.944 | 0.912 | 0.944 | 0.944 | 1.000 | – | – | 2.833 | 16575.389 |
| no_verify | manual | 6 | 1.000 | 0.917 | 1.000 | 1.000 | 1.000 | – | – | 3.000 | 11205.500 |
| no_verify | synthetic | 6 | 1.000 | 0.917 | 1.000 | 1.000 | – | – | – | 2.833 | 23254.167 |
| no_verify | zalo | 6 | 0.833 | 0.900 | 0.833 | 0.833 | – | – | – | 2.667 | 15266.500 |

Cách đọc: mỗi chỉ số là trung bình trên các câu áp dụng được (bỏ giá trị trống): Citation P chỉ tính câu có trích dẫn; Faithfulness chỉ tính câu được trả lời; Correctness chỉ tính câu có đáp án mẫu (không có câu Zalo). Đọc kèm cột "Trả lời". Cột ms có cache LLM, không dùng để so latency (đo riêng bằng `run --cache-dir <thư mục mới>`).
Cảnh báo: các run phủ số câu khác nhau {'baseline': 19, 'full': 19, 'no_grading': 19, 'no_router': 19, 'no_verify': 18}; chạy `report --common` để so trên cùng tập câu.

| run | n | Trung vị (s) | p90 (s) | LLM/câu | Bỏ (trúng cache) |
|---|---|---|---|---|---|
| full | 18 | 15.86 | 26.26 | 3.8 | 1 |
| baseline | 19 | 6.87 | 11.95 | 1.0 | 0 |
| no_router | 18 | 12.74 | 25.35 | 3.2 | 1 |
| no_grading | 18 | 8.84 | 21.21 | 2.9 | 1 |
| no_verify | 18 | 10.95 | 30.02 | 2.8 | 0 |

Không dùng cache LLM; đã trừ thời gian chờ giãn cách RPM của free tier; gồm cả truy xuất và rerank trên CPU.
