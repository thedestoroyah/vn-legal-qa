# Chốt trước: tập kiểm thử giữ riêng (held-out) 30 câu

Ngày chốt: 03/11/2026, trước khi chạy hệ thống trên bất kỳ câu nào dưới đây.

## Mục đích

1. Kiểm tra tác dụng của router (RQ3) ở đúng loại câu mà router xử lý: `temporal` (trích ngày sự việc) và `direct` (tra thẳng Điều). Trên 179 câu cũ, chênh lệch full − no_router dồn vào 12 câu temporal (correctness −0,292) và 5 câu direct (−0,100); câu situational gần 0.
2. Tăng mẫu RQ4 từ 12 lên 32 câu temporal.
3. Giảm giới hạn "prompt được chỉnh sau khi thấy tập kiểm thử": các câu này viết sau khi đã chốt prompt.

## Thiết kế

- **30 câu**, mã `M_038`–`M_067`, `source = "manual"`:
  - 20 câu `temporal` = 10 chủ đề × 2 phiên bản (`M_038`–`M_057`): mỗi chủ đề một câu có ngày sự việc trước 01/01/2021 (căn cứ BLLĐ 2012) và một câu sau (căn cứ BLLĐ 2019). Chỉ chọn quy định **khác nhau thật** giữa hai phiên bản (đã đối chiếu văn bản, loại 2 chủ đề có cùng đáp án ở cả hai bản: nghỉ bù khi ngày nghỉ hằng tuần trùng lễ, tạm ứng lương khi nghỉ hằng năm). Không trùng 6 chủ đề của 12 câu temporal cũ. Câu hỏi không nêu tên phiên bản bộ luật.
  - 10 câu `direct` (`M_058`–`M_067`): đủ 5 văn bản (gồm 1 câu hỏi thẳng BLLĐ 2012 đã hết hiệu lực), nhiều dạng hỏi (cấp Điều, cấp Khoản, cấp điểm, hỏi nội dung cụ thể). Một số Điều đã xuất hiện trong câu situational cũ; chấp nhận vì câu direct kiểm nhánh lookup_article chứ không kiểm truy xuất.
- **Người soạn**: Claude (LLM) soạn nháp từ văn bản luật trong kho, **không chạy hệ thống** trên câu nào trước khi chốt; Đạt kiểm và sửa (`checked_by = "Dat"`, `drafted_by = "Claude"`). Ghi rõ trong báo cáo.

## Mốc đóng băng

- Code và prompt: commit `caa4f2f`. Không sửa prompt cho tới khi báo cáo xong kết quả tập này.
- Sau khi Đạt duyệt và commit câu vào `eval/manual_cases.json`: không sửa, không bỏ câu nào sau khi đã chạy, trừ lỗi dữ liệu thuần túy (sai mã căn cứ do gõ nhầm), ghi lại trong báo cáo.

## Chạy và phân tích (định trước)

- RQ3: 5 cấu hình trên 30 câu mới; RQ4: 3 chính sách trên 20 câu temporal mới. Chấm bằng bộ chấm Groq như cũ.
- Báo cáo **tách riêng** tập giữ riêng (danh sách id chốt trong `eval/results/subset_rq3_30.json` và `subset_rq4_20.json`, dùng qua `--subset 30` / `--subset 20`) **và** tập gộp (209 câu RQ3, 32 câu RQ4).
- So sánh ghép cặp theo câu, bootstrap 95% (`report --ci`).
- Giả thuyết: (H1) no_router kém full về correctness và đúng phiên bản trên câu temporal + direct; (H2) RQ4: `event` > `current` và `event` > `any` về đúng phiên bản. Báo cáo kết quả dù ủng hộ hay bác bỏ giả thuyết.

## Ghi chú duyệt (03/11/2026, Đạt)

Đạt kiểm cả 30 câu, giữ 30/30. Sửa trước khi chốt:
- M_044: đáp án thêm ngoại lệ — sa thải vẫn có thể nếu hành vi đồng thời gây thiệt hại nghiêm trọng (khoản 1 Điều 126 BLLĐ 2012); bản nháp kết luận quá tuyệt đối.
- M_056: đáp án thu hẹp vào phạm vi khoản 2 Điều 29 (không suy ra nghĩa vụ báo trước, bồi thường). Không nhận đề xuất đưa "theo khoản 2 Điều 29 BLLĐ 2012" vào câu hỏi vì làm lộ phiên bản, biến câu temporal thành direct.
- M_053: câu hỏi thêm điều kiện "đã tìm mọi biện pháp khắc phục" (khoản 4 Điều 97 BLLĐ 2019).
- M_054, M_043: đáp án làm rõ (không phải tạm hoãn đương nhiên; phạm vi thông tin theo khoản 2 Điều 16).
- M_066: câu hỏi ghi rõ số hiệu Luật số 10/2012/QH13; giữ câu hỏi thẳng vào văn bản đã hết hiệu lực.
- Đáp án mẫu giữ ngắn (kết luận + điều kiện chính), không thêm câu rào đón, vì bộ chấm correctness coi mọi ý trong đáp án mẫu là ý chính.
