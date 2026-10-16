| id | type | route | refused | cited | gold | hit | LLM | ms |
|---|---|---|---|---|---|---|---|---|
| Z_0505153d | situational | situational | False | LDN2020_Dieu47 | LDN2020_Dieu47 | True | 4 | 16308 |
| Z_06847bf5 | situational | situational | False | BLDS2015_Dieu571 | BLDS2015_Dieu571 | True | 4 | 35011 |
| Z_08683040 | situational | situational | False | BLDS2015_Dieu13, BLDS2015_Dieu585 | BLDS2015_Dieu418 | False | 4 | 17397 |
| TM_001 | situational | direct | False | LTM2005_Dieu3 | LTM2005_Dieu3 | True | 3 | 12486 |
| TM_002 | situational | situational | False | LTM2005_Dieu12, LTM2005_Dieu13, LTM2005_Dieu3 | LTM2005_Dieu3 | True | 4 | 48720 |
| TM_003 | situational | situational | False | LTM2005_Dieu16, LTM2005_Dieu6 | LTM2005_Dieu6 | True | 4 | 24685 |
| X_direct | direct | direct | False | BLDS2015_Dieu357 | BLDS2015_Dieu357 | True | 3 | 9556 |
| X_temporal | temporal | situational | False | BLLD2019_Dieu35 | BLLD2019_Dieu35 | True | 4 | 55554 |
| X_oos | out_of_scope | out_of_scope | True |  |  | True | 1 | 4194 |
| X_oos2 | out_of_scope | out_of_scope | True |  |  | True | 1 | 4176 |

Đúng ở cấp Điều (hoặc từ chối đúng): 9/10

## Ghi chú lỗi prompt
Chạy 16/10/2026, cấu hình full, gemini-3.1-flash-lite, biến thể clause_header. 10 câu: 3 zalo, 3 synthetic, 4 manual bù bằng EXTRA (Hùng chưa nộp câu manual). 9/10 đúng; 3-4 lượt LLM mỗi câu (1 lượt với câu từ chối); ~4-55 s mỗi câu, phần lớn là rerank và giãn cách 4,2 s giữa các lượt gọi.

- Z_08683040: truy xuất — gold Zalo là BLDS Điều 418, top-5 không có; câu trả lời dựa Điều 13 và 585 nghe hợp lý. Lỗi nằm ở truy xuất/nhãn Zalo chứ không phải prompt; để phân tích ở Sprint 5.
- TM_001: route — câu synthetic "Theo Luật Thương mại 2005, hoạt động thương mại được định nghĩa như thế nào?" được gán `direct` (Điều 3) dù không nêu số Điều; kết quả đúng nhưng nhờ bước đoán. Chỉ 1 lần nên chưa sửa prompt; theo dõi khi chạy đủ tập.
- grade: 10/10 câu trả về `sufficient = true`, vòng viết lại chưa được thử bằng LLM thật (đã có test với LLM giả). Nếu chạy đủ tập mà vẫn không kích hoạt, nới tiêu chí trong GRADE_RULES.
- verify: không gỡ trích dẫn nào ở 8 câu có trích dẫn; chưa quan sát nhánh gỡ/sinh lại trên LLM thật.
- X_temporal: route đặt `event_date = 2022-07-01` đúng quy ước "chỉ có năm"; truy xuất lọc đúng BLLĐ 2019.
- Chưa sửa prompt (quy tắc: chỉ sửa khi lỗi lặp lại từ 2 câu); đã dùng 1 vòng chạy, ~45 lượt Gemini.
