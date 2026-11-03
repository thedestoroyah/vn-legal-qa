# Thang chấm tay 3 mức (H11)

Dùng cho H14: Đạt và Hùng **chấm độc lập** cùng một tập khoảng 20 câu trả lời của tác tử, sau đó so với bộ chấm LLM (`eval/judge.py`) để kiểm định bộ chấm (spec mục 7, đề cương mục 8).

- Định nghĩa **giống `JUDGE_RULES`** trong `eval/judge.py` (theo RAGAS, Es và cộng sự, 2024), cộng các điểm làm rõ đã đề xuất trong `docs/judge_review.md`. Nếu Đạt sửa prompt chấm thì sửa file này theo.
- Chấm theo **nội dung pháp lý**: không trừ điểm vì diễn đạt khác, câu dài hơn, thêm chữ nối hay văn phong.
- Điểm chỉ nhận một trong 3 giá trị: **0**, **0,5**, **1** (trong CSV có thể ghi `0.5` hoặc `0,5`).

## 1. Faithfulness (độ trung thành với ngữ cảnh)

**Câu hỏi khi chấm:** mọi khẳng định trong câu trả lời có suy ra được từ cột `contexts` (các đoạn tác tử đã dùng) không? **Không** nhìn đáp án mẫu khi chấm tiêu chí này.

- **Ý chính** là phần trả lời trực tiếp câu hỏi: kết luận (được/không được, có/không) và con số, thời hạn, điều kiện mà câu hỏi hỏi tới. Câu giải thích thêm, hệ quả, lời khuyên là **chi tiết phụ**.
- **Suy ra trực tiếp** là diễn đạt lại, hoặc rút ra kết luận logic từ đoạn trích mà không cần kiến thức ngoài đoạn trích.

| Điểm | Mô tả | Ví dụ |
|---|---|---|
| **1** | Mọi khẳng định đều có trong đoạn trích hoặc suy ra trực tiếp từ đoạn trích. | **Z_0505153d** — *Hỏi:* Thành viên chưa góp đủ vốn đã cam kết thì công ty TNHH đăng ký thay đổi vốn điều lệ thời hạn bao lâu? *Trả lời:* "Công ty phải đăng ký thay đổi vốn điều lệ và tỷ lệ phần vốn góp của các thành viên trong thời hạn 30 ngày kể từ ngày cuối cùng phải góp đủ phần vốn góp [LDN2020_Dieu47_Khoan4]." *Căn cứ:* `LDN2020_Dieu47_Khoan4` "...công ty phải đăng ký thay đổi vốn điều lệ, tỷ lệ phần vốn góp... trong thời hạn 30 ngày kể từ ngày cuối cùng phải góp đủ phần vốn góp..." *Lý do:* nội dung và con số 30 ngày khớp đoạn trích. |
| **0,5** | Ý chính có căn cứ, nhưng có chi tiết phụ không có trong đoạn trích và không suy ra trực tiếp được. | **Ví dụ minh họa** (dựa trên `BLDS2015_Dieu640_Khoan1`) — *Hỏi:* Người lập di chúc có được sửa di chúc đã lập không? *Trả lời:* "Có, người lập di chúc có thể sửa đổi, bổ sung, thay thế, hủy bỏ di chúc vào bất cứ lúc nào [BLDS2015_Dieu640_Khoan1]. Việc sửa đổi phải được công chứng mới có hiệu lực." *Căn cứ:* "Người lập di chúc có thể sửa đổi, bổ sung, thay thế, huỷ bỏ di chúc đã lập vào bất cứ lúc nào." *Lý do:* ý chính (được sửa, bất cứ lúc nào) có căn cứ; câu về công chứng là chi tiết phụ không có trong đoạn trích. |
| **0** | Ý chính không có trong đoạn trích, hoặc mâu thuẫn với đoạn trích. | **Ví dụ minh họa** (dựa trên `BLDS2015_Dieu640_Khoan1`) — *Hỏi:* Người lập di chúc được thay đổi di chúc bao nhiêu lần? *Trả lời:* "Người lập di chúc chỉ được sửa đổi di chúc tối đa 2 lần [BLDS2015_Dieu640_Khoan1]." *Căn cứ:* "...vào bất cứ lúc nào." *Lý do:* kết luận "tối đa 2 lần" mâu thuẫn với đoạn trích. |

> Dữ liệu chạy thật hiện chưa có câu nào bị chấm faithfulness = 0, nên ví dụ mức 0 và 0,5 là ví dụ minh họa dựng trên điều luật thật. Sau H14, thay bằng ví dụ thật nếu có.

**Ca biên đã thấy trong dữ liệu thật:** `Z_7ae82e65` (*Hỏi:* di chúc được thay đổi bao nhiêu lần?) trả lời "...vào bất cứ lúc nào [BLDS2015_Dieu640_Khoan1]. Pháp luật không giới hạn số lần thực hiện các hành vi này." Bộ chấm LLM cho 0,5. Theo định nghĩa "suy ra trực tiếp" ở trên ("bất cứ lúc nào" → "không giới hạn số lần"), thang này cho **1**. Đây là chỗ cần chốt với Đạt (`docs/judge_review.md` mục 2.1–2.2).

## 2. Answer Correctness (độ đúng so với đáp án mẫu)

**Câu hỏi khi chấm:** câu trả lời có khớp cột `reference_answer` về **kết luận, điều kiện, con số, thời hạn** không? Thêm thông tin đúng không bị trừ. `reference_answer` trống (câu Zalo) thì **để trống** ô correctness.

| Điểm | Mô tả | Ví dụ thật |
|---|---|---|
| **1** | Khớp mọi ý chính của đáp án mẫu. | **TM_001** — *Hỏi:* Theo Luật Thương mại 2005, hoạt động thương mại được định nghĩa như thế nào? *Đáp án mẫu:* "Hoạt động nhằm mục đích sinh lợi, bao gồm mua bán hàng hoá, cung ứng dịch vụ, đầu tư, xúc tiến thương mại và các hoạt động nhằm mục đích sinh lợi khác." *Trả lời:* "Hoạt động thương mại là hoạt động nhằm mục đích sinh lợi, bao gồm mua bán hàng hoá, cung ứng dịch vụ, đầu tư, xúc tiến thương mại và các hoạt động nhằm mục đích sinh lợi khác [LTM2005_Dieu3]." *Lý do:* khớp hoàn toàn. |
| **0,5** | Đúng kết luận nhưng thiếu hoặc sai một điều kiện, con số, thời hạn. | **LD_015** — *Hỏi:* Lao động nữ được nghỉ thai sản bao lâu khi sinh một con? *Đáp án mẫu:* "06 tháng (trước và sau khi sinh); thời gian nghỉ trước khi sinh không quá 02 tháng." *Trả lời:* "Lao động nữ được nghỉ thai sản trước và sau khi sinh con là 06 tháng [BLLD2019_Dieu139_Khoan1]." *Lý do (theo bộ chấm LLM):* đúng 06 tháng nhưng thiếu điều kiện "trước khi sinh không quá 02 tháng". *(Ca biên, xem quy tắc R5.)* |
| **0** | Sai kết luận, hoặc không trả lời câu hỏi. | **M_018** (cấu hình baseline) — *Hỏi:* Năm 2019, tôi làm HĐLĐ xác định thời hạn 24 tháng, muốn đơn phương chấm dứt khi không có lý do luật định mà chỉ báo trước 30 ngày có được không? *Đáp án mẫu:* "Không được, theo BLLĐ 2012 phải có một trong các lý do luật định và báo trước." *Trả lời:* "Có, bạn có quyền đơn phương chấm dứt hợp đồng... nếu báo trước ít nhất 30 ngày [BLLD2019_Dieu35_Khoan1]." *Lý do:* kết luận ngược đáp án (dùng BLLĐ 2019 cho sự việc năm 2019). Câu này **faithfulness = 1** vì đúng với đoạn trích: hai tiêu chí độc lập. |

## 3. Quy tắc biên

| # | Trường hợp | Faithfulness | Correctness |
|---|---|---|---|
| R1 | Từ chối **đúng** (câu out_of_scope bị từ chối) | không áp dụng (để trống) | **1** |
| R2 | Từ chối **sai** (câu trong phạm vi bị từ chối, có đáp án mẫu) | không áp dụng | **0** |
| R3 | Trả lời câu out_of_scope (đáng lẽ phải từ chối) | không áp dụng | **0** |
| R4 | Đúng kết luận nhưng sai hoặc thiếu điều kiện, con số mà câu hỏi hỏi tới | chấm bình thường | **0,5** |
| R5 | Thiếu một chi tiết có trong đáp án mẫu nhưng câu hỏi **không hỏi** tới và không làm đổi kết luận | chấm bình thường | **1** *(đề xuất, chờ chốt với Đạt)* |
| R6 | Câu gắn nhãn "(chưa có căn cứ)" | chấm như mọi khẳng định: nội dung không có trong đoạn trích → ý chính 0, chi tiết phụ 0,5. Nhãn không cộng/trừ thêm | chấm theo nội dung |
| R7 | Nội dung có trong ngữ cảnh nhưng **gắn sai mã** trích dẫn | không trừ (Citation Precision đo riêng) | chấm theo nội dung |
| R8 | Đúng nhờ kiến thức ngoài, đoạn trích không chứa căn cứ | 0 hoặc 0,5 | có thể 1 |
| R9 | Dùng sai phiên bản văn bản (vd. BLLĐ 2019 cho sự việc 2019), nhưng đúng với đoạn trích | không trừ (RQ4 đo riêng) | theo đáp án mẫu (thường 0) |
| R10 | Trả lời một phần, phần còn lại ghi "không đủ căn cứ" | phần "không đủ căn cứ" không phải khẳng định, không trừ | thường 0,5 |
| R11 | Câu tra cứu trực tiếp (direct): `contexts` là toàn văn Điều | chấm theo toàn văn Điều | bình thường |

R1–R3 bộ chấm đã xử lý bằng code (`judge()` trong `eval/judge.py`), nhưng người chấm vẫn điền để tính tỷ lệ khớp cho đủ.

## 4. Quy tắc làm việc

1. Mỗi người chép phiếu gốc `eval/results/grading_rq3.csv` thành file riêng: `grading_rq3_hung.csv`, `grading_rq3_dat.csv`.
2. **Chấm độc lập:** không xem phiếu của người kia, không xem `eval/results/agent_rq3_judge.jsonl` (điểm LLM) trước khi cả hai chấm xong.
3. Chấm faithfulness chỉ nhìn `answer` + `contexts`; chấm correctness chỉ nhìn `answer` + `reference_answer`.
4. Câu nào phân vân thì ghi lý do vào cột `note` (vd. "R5?"), không bàn với người kia trong lúc chấm.
5. Chấm xong mới so sánh. Câu lệch giữa hai người thì thảo luận để rút kinh nghiệm cho rubric, **nhưng không sửa điểm đã chấm** (tỷ lệ khớp tính trên điểm gốc).

## 5. Mẫu bảng chấm

Phiếu CSV do `python -m eval.agent_eval sheet` tạo có các cột `id, question, answer, contexts, reference_answer, faithfulness, correctness, note`. Bảng tổng hợp sau khi chấm:

| id | faithfulness | correctness | ghi chú | người chấm |
|---|---|---|---|---|
| LD_015 | 1 | 0,5 | thiếu "trước sinh ≤ 02 tháng" (R4/R5?) | Hùng |
| … | | | | |

## 6. Chấm thử theo thang (mẫu giao diện)

| Mẫu | Faithfulness | Correctness | Lý do |
|---|---|---|---|
| `src/ui/samples/answered.json` | 1 | không có đáp án mẫu | Cả hai câu đều có trong `BLDS2015_Dieu357_Khoan1`, `_Khoan2`. |
| `src/ui/samples/partial.json` | 0,5 | không có đáp án mẫu | Ý chính "phải trả lãi" có căn cứ; câu "lãi suất luôn cố định 20% một năm (chưa có căn cứ)" không có trong đoạn trích → R6. Nếu coi lãi suất là ý chính của câu hỏi thì 0. |

Đạt chấm thử độc lập 2 mẫu này. Hai người ra cùng điểm thì coi như đã thống nhất cách hiểu thang.

## 7. Kết quả kiểm định *(điền ở H14)*

- Số câu chấm: …
- Tỷ lệ khớp Hùng – LLM: faithfulness … / correctness …
- Tỷ lệ khớp Đạt – LLM: faithfulness … / correctness …
- Tỷ lệ khớp Hùng – Đạt: faithfulness … / correctness … (số ô giống nhau / số ô cả hai cùng có điểm)
- Lệnh: `python -m eval.agent_eval agree --rq rq3 --filled eval/results/grading_rq3_hung.csv` (tương tự với `_dat.csv`).
- Ví dụ LLM chấm lệch (2–3 câu): …

