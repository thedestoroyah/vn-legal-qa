# Công cụ tạo báo cáo tuần

Tạo 3 file báo cáo (docx, pptx, xlsx) từ một file nội dung `content.json`, theo thiết kế bộ giữa kỳ KLTN của Đạt.

| File | Việc |
|---|---|
| `build_docx.py` | Báo cáo Word: dùng file mẫu KLTN làm khuôn (bìa, style, lề), thay nội dung |
| `build_pptx.js` | Slide (pptxgenjs): tái hiện thiết kế slide giữa kỳ KLTN; logo ở `logo.png` |
| `build_xlsx.py` | Kế hoạch Excel: khuôn file KLTN, tuần 1–10 lấy nguyên văn từ `Mid_Term/KẾ HOẠCH.xlsx` |
| `outline_to_md.py` | Chuyển đề cương `.txt` (xuất từ Google Docs) sang Markdown |
| `topdf.sh` | Render docx/pptx/xlsx ra PDF bằng OnlyOffice `x2t` để xem trước (máy không có LibreOffice) |

Tuần mới: chép `Week 26.10-01.11/content.json` sang thư mục tuần mới, sửa nội dung, rồi chạy (cần Python có `python-docx`, `openpyxl` và `npm install pptxgenjs` trong thư mục làm việc):

```bash
REF=~/"0. Ton_Duc_Thang_University/HK7/Graduation_Thesis/vn-legal-verify/docs/managements"   # file mẫu KLTN (ngoài repo, chuyển chỗ 11/2026)
W="docs/managements/Week <dd.mm-dd.mm>"
python docs/managements/tools/build_docx.py "$REF/Mid_Term/Báo cáo giữa kỳ - KLTN.docx" "$W/Báo cáo tuần N - ĐA127.docx" "$W/content.json"
node docs/managements/tools/build_pptx.js "$W/Slide báo cáo tuần N - ĐA127.pptx" docs/managements/tools/logo.png "$W/content.json"
python docs/managements/tools/build_xlsx.py "$REF/KẾ HOẠCH - KLTN.xlsx" "docs/managements/Mid_Term/KẾ HOẠCH.xlsx" "$W/KẾ HOẠCH tuần N - ĐA127.xlsx"
```

Giới hạn: `build_docx.py` chọn đoạn mẫu theo vị trí trong file KLTN (chỉ số 39–52); `build_xlsx.py` và `build_pptx.js` còn ghi cứng một số chữ của tuần 11 (tiêu đề, ghi chú, slide tổng quan) — sửa trong script khi làm tuần khác.

Từ tuần 12: slide và kế hoạch Excel của mỗi tuần dùng script riêng trong thư mục tuần (`Week <...>/build_pptx.js`, `build_xlsx.py`, chép từ tuần trước rồi sửa), vì nội dung từng slide khác nhau mỗi tuần; `build_pptx.js` tuần 12 nhận thêm đối số thứ 4 là ảnh chụp giao diện. `build_docx.py` dùng chung, ngày ký lấy từ `meta.date`. Script ở `tools/` là bản của tuần 11.
Môi trường tạm: `python -m venv <tmp>/officevenv && <tmp>/officevenv/bin/pip install python-docx openpyxl`; `npm install pptxgenjs@3.12.0` trong một thư mục tạm rồi chạy node với `NODE_PATH=<thư mục>/node_modules`.

Từ tuần 13: file mẫu `KẾ HOẠCH - KLTN.xlsx` bên dự án KLTN đã đổi ngày 06/11 (commit `a0041cf` của repo `vn-legal-verify`: thêm ô gộp, đổi chiều cao hàng), làm bảng kế hoạch dàn thành 5 trang. Dùng bản trước đó (dựng lại tuần 12 khớp từng ô): `git -C <repo vn-legal-verify> show "2a13ff0:docs/managements/KẾ HOẠCH - KLTN.xlsx" > <tmp>/kltn_plan.xlsx` rồi truyền `<tmp>/kltn_plan.xlsx` thay cho `$REF/KẾ HOẠCH - KLTN.xlsx`. Mẫu docx (`Mid_Term/Báo cáo giữa kỳ - KLTN.docx`) không đổi. Slide tuần 13 nhận 2 ảnh: `node build_pptx.js <out.pptx> <logo.png> <content.json> <ảnh 3 trang báo cáo.png> <sơ đồ kiến trúc.png>`.

Từ tuần 14: thư mục tuần `Week 16.11-22.11/` (nội dung 16/11 – 19/11). Slide nhận 1 ảnh: `node build_pptx.js <out.pptx> <logo.png> <content.json> <ảnh Bảng 5.4 cắt từ PDF báo cáo.png>` (ảnh 948×381 cắt từ bản render). Mẫu Excel vẫn lấy bản `2a13ff0`; mẫu docx `Mid_Term/Báo cáo giữa kỳ - KLTN.docx` ở repo `vn-legal-verify` (`~/0. Ton_Duc_Thang_University/HK7/Graduation_Thesis/vn-legal-verify/docs/managements/`). Đạt sửa tay cả 3 file tuần 14 sau khi build nên `content.json` tuần 14 có thể không khớp hẳn: khi làm tuần 15 đọc nội dung từ 3 file đã nộp, đừng build lại tuần 14.

`topdf.sh` cần bộ đệm font của OnlyOffice còn đúng: sau khi đổi gói font hệ thống (19/11: `ttf-ms-fonts` sang `ttf-ms-win11-auto`, tên file đổi hoa/thường như `Times.TTF` thành `times.ttf`) x2t báo `DoctRenderer: error code="calculate"` với mọi file, và `build_report.py` chỉ cảnh báo, để trống số trang danh mục hình/bảng. Cách sửa chưa kiểm: mở OnlyOffice Desktop một lần để nó tạo lại `~/.local/share/onlyoffice/desktopeditors/data/fonts/AllFonts.js`. Cách đã kiểm 19/11 (không sửa dữ liệu của OnlyOffice): chép `AllFonts.js` và `font_selection.bin` trong thư mục đó sang thư mục tạm, thay các đường dẫn font đã đổi hoa/thường bằng đường dẫn thật (cùng độ dài, thay bằng byte), rồi chạy x2t với `m_sAllFontsPath` trỏ vào bản vá (bản sao của `topdf.sh`).
