# Góp ý prompt chấm `JUDGE_RULES` (H10')

Người duyệt: Hùng · Ngày: 29/10/2026 · Đối tượng: `JUDGE_ROLE` + `JUDGE_RULES` trong `eval/judge.py`.
Mục đích: bảo đảm bộ chấm LLM và thang chấm tay (`docs/rubric.md`) **dùng cùng định nghĩa**, để tỷ lệ khớp người–LLM ở H14 có ý nghĩa.

> Theo quy ước nhóm, Hùng chỉ góp ý; Đạt quyết định và sửa `eval/judge.py`.

## 1. Kết luận chung

- Định nghĩa hai tiêu chí **đúng tinh thần RAGAS** (Es và cộng sự, 2024): faithfulness so câu trả lời với ngữ cảnh, không so với đáp án; correctness so với đáp án mẫu. Thang 3 mức 0 / 0,5 / 1 và việc chấm từ chối / ngoài phạm vi bằng code là hợp lý.
- Khác biệt chính so với RAGAS: RAGAS tính faithfulness = tỷ lệ khẳng định được hỗ trợ (liên tục 0–1), còn ở đây rút gọn thành 3 mức theo "ý chính / chi tiết phụ". Vì vậy **ranh giới "ý chính" và "chi tiết phụ" phải được định nghĩa rõ**, nếu không người và LLM sẽ lệch nhau chủ yếu ở mức 0,5 (xem mục 2.1).
- `docs/rubric.md` đã được viết theo đúng `JUDGE_RULES` hiện tại cộng các đề xuất ở mục 2. Nếu Đạt không nhận đề xuất nào thì Hùng sẽ sửa lại rubric cho khớp.

## 2. Chỗ mơ hồ và đề xuất sửa

### 2.1 "Ý chính" và "chi tiết phụ" chưa được định nghĩa (quan trọng nhất)

Hiện tại: `0.5: ý chính có căn cứ nhưng có chi tiết phụ không có trong đoạn trích`.

Đề xuất thêm một dòng định nghĩa:
```text
"Ý chính" là phần trả lời trực tiếp câu hỏi: kết luận (được/không được, có/không) và con số, thời hạn, điều kiện mà câu hỏi hỏi tới. Các câu giải thích thêm, hệ quả, lời khuyên là "chi tiết phụ".
```

Ví dụ thật cho thấy cần quy tắc này: câu `Z_7ae82e65` (di chúc thay đổi bao nhiêu lần), bộ chấm cho faithfulness **0,5** vì câu "Pháp luật không giới hạn số lần thực hiện các hành vi này" không có nguyên văn trong đoạn trích. Nhưng đoạn trích `BLDS2015_Dieu640_Khoan1` ghi "vào bất cứ lúc nào", và câu kia lại chính là câu trả lời cho câu hỏi "bao nhiêu lần". Như vậy cần xác định: đây là ý chính được **suy ra trực tiếp** (1 điểm) hay là chi tiết phụ không có căn cứ (0,5)?

### 2.2 Thế nào là "suy ra trực tiếp"

Đề xuất thêm:
```text
"Suy ra trực tiếp" = diễn đạt lại hoặc rút ra kết luận logic từ một đoạn trích mà không cần kiến thức ngoài đoạn trích (ví dụ: "vào bất cứ lúc nào" → "không giới hạn số lần"). Kết luận cần thêm quy định khác (điều luật không có trong đoạn trích, kiến thức chung) thì KHÔNG phải suy ra trực tiếp.
```

### 2.3 Câu gắn nhãn "(chưa có căn cứ)"

Hiện tại: "Câu gắn nhãn '(chưa có căn cứ)' vẫn là khẳng định cần kiểm." Câu này chưa nói câu đó ảnh hưởng tới điểm thế nào. Đề xuất ghi rõ:
```text
Câu gắn nhãn "(chưa có căn cứ)" chấm như mọi khẳng định khác: nếu nội dung của nó không có trong đoạn trích thì tính là khẳng định không có căn cứ (ý chính → 0, chi tiết phụ → 0.5). Nhãn này không được cộng hay trừ thêm điểm.
```
(Lý do: tác tử tự gắn nhãn là hành vi tốt về mặt trung thực, nhưng faithfulness đo nội dung câu trả lời, không đo việc gắn nhãn. Nếu nhóm muốn thưởng hành vi này thì nên đo bằng chỉ số riêng, không trộn vào faithfulness.)

### 2.4 Correctness: thiếu chi tiết mà câu hỏi không hỏi

Ví dụ thật `LD_015`: câu hỏi "nghỉ thai sản bao lâu khi sinh một con?", câu trả lời "06 tháng" (đúng), nhưng thiếu ý "nghỉ trước khi sinh không quá 02 tháng" có trong đáp án mẫu. Bộ chấm cho **0,5**. Người chấm có thể cho 1 vì câu hỏi chỉ hỏi "bao lâu".

Đề xuất thêm:
```text
Chỉ trừ xuống 0.5 khi thiếu/sai một điều kiện, con số, thời hạn mà câu hỏi hỏi tới hoặc làm thay đổi kết luận. Thiếu một chi tiết bổ sung có trong đáp án mẫu nhưng câu hỏi không hỏi thì vẫn 1.
```
Nếu nhóm muốn chấm chặt (thiếu bất kỳ ý nào trong đáp án mẫu → 0,5) thì cũng được, nhưng phải ghi rõ trong cả prompt lẫn rubric.

### 2.5 Ví dụ trong prompt chưa tách bạch hai tiêu chí

Cả 2 ví dụ hiện có đều có faithfulness = correctness (1/1 và 0,5/0,5). Bộ chấm dễ "học" rằng hai điểm đi cùng nhau. Đề xuất thêm **Ví dụ 3** lấy từ dữ liệu thật (`M_018`, cấu hình baseline): câu trả lời trung thành với đoạn trích nhưng sai kết luận vì dùng nhầm văn bản hết hiệu lực/còn hiệu lực:
```text
Ví dụ 3:
Đoạn trích: [BLLD2019_Dieu35_Khoan1] Người lao động có quyền đơn phương chấm dứt hợp đồng lao động nhưng phải báo trước cho người sử dụng lao động như sau: ... b) Ít nhất 30 ngày nếu làm việc theo hợp đồng lao động xác định thời hạn có thời hạn từ 12 tháng đến 36 tháng;
Câu hỏi: Năm 2019, tôi làm hợp đồng xác định thời hạn 24 tháng. Tôi muốn đơn phương chấm dứt hợp đồng khi không có lý do luật định mà chỉ báo trước 30 ngày có được không?
Câu trả lời cần chấm: Có, bạn có quyền đơn phương chấm dứt hợp đồng nếu báo trước ít nhất 30 ngày [BLLD2019_Dieu35_Khoan1].
Đáp án mẫu: Không được, theo BLLĐ 2012 người lao động làm hợp đồng xác định thời hạn khi đơn phương chấm dứt phải có một trong các lý do luật định và báo trước.
{"faithfulness": 1, "correctness": 0, "reason": "Câu trả lời đúng với đoạn trích nhưng kết luận trái với đáp án mẫu (năm 2019 áp dụng BLLĐ 2012)."}
```
Ví dụ này còn giúp bộ chấm hiểu rằng **faithfulness không phạt việc dùng sai phiên bản văn bản**. Sai phiên bản đã được đo riêng bằng "tỷ lệ đúng phiên bản" (RQ4).

## 3. Trường hợp biên chưa có quy tắc

| # | Trường hợp | Đề xuất xử lý | Ghi chú |
|---|---|---|---|
| B1 | Nội dung đúng và có trong đoạn trích, nhưng **mã trích dẫn gắn sai** Khoản/Điều (vd. ý của Khoản 2 lại gắn `[..._Khoan1]`) | faithfulness chấm theo **toàn bộ ngữ cảnh**, không theo từng mã → không trừ. Sai mã đã được đo bằng Citation Precision. | Cần ghi một câu vào prompt để bộ chấm không tự trừ. |
| B2 | Câu trả lời đúng nhờ **kiến thức ngoài** đoạn trích (đoạn trích không chứa căn cứ) | faithfulness thấp (0 hoặc 0,5), correctness vẫn có thể là 1. | Thuộc định nghĩa hiện tại, nhưng nên nêu rõ như một ví dụ. |
| B3 | Câu trả lời từ chối **một phần** (trả lời được một ý, ý còn lại ghi không đủ căn cứ) | Không phải `refused` → LLM chấm. Phần "không đủ căn cứ" không phải khẳng định nên không trừ faithfulness; correctness theo phần đã trả lời (thường 0,5). | |
| B4 | Nhánh `lookup_article` (câu tra cứu trực tiếp): ngữ cảnh là **cả Điều** | Hợp lý, vì `used_contexts` đã lấy bản Điều. Chỉ cần ghi chú cho người chấm tay rằng cột `contexts` của câu direct là toàn văn Điều. | |
| B5 | Câu trả lời **trích nguyên văn** điều luật rất dài nhưng không trực tiếp kết luận | faithfulness 1; correctness 0,5 nếu đáp án mẫu yêu cầu kết luận rõ (được/không). | |
| B6 | Câu Zalo không có đáp án mẫu | correctness = null (đã có). Người chấm tay để trống ô. | Đã thống nhất. |

## 4. Quan sát từ kết quả bộ chấm hiện có (`eval/results/agent_rq3_judge.jsonl`)

- Cấu hình `full`: 65/66 câu được chấm faithfulness có điểm **1**, chỉ 1 câu được 0,5, không câu nào 0. Cấu hình `baseline` cũng gần như toàn 1.
- Điểm dồn sát mức trần như vậy có thể do tác tử thật sự trung thành (verify đã gỡ câu không có căn cứ), hoặc do bộ chấm dễ dãi. **Bước chấm tay H14 là cách duy nhất phân biệt hai khả năng này.** Đề xuất khi chọn 20 câu cho phiếu chấm, nếu được thì ưu tiên lấy thêm vài câu baseline/no_verify, vì ở đó dễ có câu không trung thành.
- Đề xuất báo cáo thêm phân bố điểm (không chỉ trung bình) trong Chương 4 để người đọc thấy hiện tượng dồn trần này.

## 5. Tóm tắt đề xuất cho Đạt

1. Thêm định nghĩa "ý chính" và "suy ra trực tiếp" (mục 2.1, 2.2).
2. Ghi rõ cách chấm câu "(chưa có căn cứ)" (mục 2.3).
3. Quy tắc trừ correctness chỉ với chi tiết câu hỏi hỏi tới (mục 2.4). Cần cả nhóm chốt chặt hay lỏng.
4. Thêm Ví dụ 3 (faithfulness 1, correctness 0) (mục 2.5).
5. Thêm 1 câu: "Không trừ faithfulness vì gắn sai mã trích dẫn khi nội dung có trong ngữ cảnh" (B1).

Nếu sửa prompt thì phải chạy lại `agent_eval judge` trước khi tính tỷ lệ khớp ở H14.

