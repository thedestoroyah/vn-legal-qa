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
REF=~/"0. Ton_Duc_Thang_University/HK7/Graduation_Thesis/Mid_Term"   # file mẫu KLTN (ngoài repo)
W="docs/managements/Week <dd.mm-dd.mm>"
python docs/managements/tools/build_docx.py "$REF/Báo cáo giữa kỳ - KLTN.docx" "$W/Báo cáo tuần N - ĐA127.docx" "$W/content.json"
node docs/managements/tools/build_pptx.js "$W/Slide báo cáo tuần N - ĐA127.pptx" docs/managements/tools/logo.png "$W/content.json"
python docs/managements/tools/build_xlsx.py "$REF/KẾ HOẠCH - KLTN.xlsx" "docs/managements/Mid_Term/KẾ HOẠCH.xlsx" "$W/KẾ HOẠCH tuần N - ĐA127.xlsx"
```

Giới hạn: `build_docx.py` chọn đoạn mẫu theo vị trí trong file KLTN (chỉ số 39–52); `build_xlsx.py` và `build_pptx.js` còn ghi cứng một số chữ của tuần 11 (tiêu đề, ghi chú, slide tổng quan) — sửa trong script khi làm tuần khác.
