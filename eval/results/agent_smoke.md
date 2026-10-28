| id | type | route | refused | cited | gold | hit | LLM | ms |
|---|---|---|---|---|---|---|---|---|
| Z_0505153d | situational | situational | False | LDN2020_Dieu47 | LDN2020_Dieu47 | True | 4 | 32605 |
| Z_06847bf5 | situational | situational | False | BLDS2015_Dieu571 | BLDS2015_Dieu571 | True | 4 | 5590 |
| Z_08683040 | situational | situational | False | BLDS2015_Dieu13, BLDS2015_Dieu585 | BLDS2015_Dieu418 | False | 4 | 4855 |
| TM_001 | situational | direct | False | LTM2005_Dieu3 | LTM2005_Dieu3 | True | 3 | 1193 |
| TM_002 | situational | situational | False | LTM2005_Dieu12, LTM2005_Dieu13, LTM2005_Dieu3 | LTM2005_Dieu3 | True | 4 | 6562 |
| TM_003 | situational | situational | False | LTM2005_Dieu16, LTM2005_Dieu6 | LTM2005_Dieu6 | True | 4 | 5547 |
| M_016 | temporal | situational | False | BLLD2012_Dieu22 | BLLD2012_Dieu22 | True | 4 | 35783 |
| M_017 | temporal | situational | False | BLLD2019_Dieu18 | BLLD2019_Dieu20 | False | 5 | 34625 |
| M_018 | temporal | situational | False | BLLD2012_Dieu37, BLLD2012_Dieu41, BLLD2012_Dieu43 | BLLD2012_Dieu37 | True | 5 | 31628 |
| M_019 | temporal | situational | False | BLLD2019_Dieu35 | BLLD2019_Dieu35 | True | 4 | 27055 |

Đúng ở cấp Điều (hoặc từ chối đúng): 8/10

## Ghi chú lỗi prompt
Lần 2 (28/10/2026): cùng cấu hình, sau khi có BLLĐ 2012 trong chỉ mục; 4 câu manual là câu temporal thật của Hùng (M_016–M_019) thay cho câu tự soạn. 8/10 đúng: trượt Z_08683040 (như lần 1, lỗi truy xuất/nhãn Zalo) và M_017.

- RQ4 hoạt động trên LLM thật: M_016 (5/2020) và M_018 (2019) chỉ trích BLLĐ 2012, M_019 (2022) trích BLLĐ 2019. Router trích ngày đúng quy ước: "tháng 5/2020" → 2020-05-15, "năm 2019" → 2019-07-01.
- grade lần đầu đề xuất viết lại truy vấn trên LLM thật (M_017, M_018: 5 lượt LLM).
- M_017: tác tử trả lời "được ký HĐ xác định thời hạn dưới 12 tháng cho việc mùa vụ" [BLLD2019_Dieu18_Khoan2]; gold là Điều 20 (loại HĐ), đáp án mẫu "không được". Đáp án mẫu gây tranh cãi (BLLĐ 2019 bỏ *loại* HĐ mùa vụ nhưng vẫn cho ký HĐ xác định thời hạn 5 tháng) → nhờ Hùng xem lại câu này; truy xuất cũng không đưa Điều 20 vào top-5.
- Chưa sửa prompt.

Lần 1 (16/10/2026):

Chạy 16/10/2026, cấu hình full, gemini-3.1-flash-lite, biến thể clause_header. 10 câu: 3 zalo, 3 synthetic, 4 manual bù bằng EXTRA (Hùng chưa nộp câu manual). 9/10 đúng; 3-4 lượt LLM mỗi câu (1 lượt với câu từ chối); ~4-55 s mỗi câu, phần lớn là rerank và giãn cách 4,2 s giữa các lượt gọi.

- Z_08683040: truy xuất — gold Zalo là BLDS Điều 418, top-5 không có; câu trả lời dựa Điều 13 và 585 nghe hợp lý. Lỗi nằm ở truy xuất/nhãn Zalo chứ không phải prompt; để phân tích ở Sprint 5.
- TM_001: route — câu synthetic "Theo Luật Thương mại 2005, hoạt động thương mại được định nghĩa như thế nào?" được gán `direct` (Điều 3) dù không nêu số Điều; kết quả đúng nhưng nhờ bước đoán. Chỉ 1 lần nên chưa sửa prompt; theo dõi khi chạy đủ tập.
- grade: 10/10 câu trả về `sufficient = true`, vòng viết lại chưa được thử bằng LLM thật (đã có test với LLM giả). Nếu chạy đủ tập mà vẫn không kích hoạt, nới tiêu chí trong GRADE_RULES.
- verify: không gỡ trích dẫn nào ở 8 câu có trích dẫn; chưa quan sát nhánh gỡ/sinh lại trên LLM thật.
- X_temporal: route đặt `event_date = 2022-07-01` đúng quy ước "chỉ có năm"; truy xuất lọc đúng BLLĐ 2019.
- Chưa sửa prompt (quy tắc: chỉ sửa khi lỗi lặp lại từ 2 câu); đã dùng 1 vòng chạy, ~45 lượt Gemini.
