"""Kế hoạch tuần 13 .xlsx: khuôn file KLTN, tuần 1–10 nguyên văn KẾ HOẠCH.xlsx của nhóm, tuần 11–12 như báo cáo tuần 11–12.

Chép từ tuần 12 (cùng bố cục: bảng tới tuần 17, tuần 16 nộp, tuần 17 phản biện); sửa tuần 13–17 và ghi chú.
  python build_xlsx.py <KẾ HOẠCH - KLTN.xlsx> <Mid_Term/KẾ HOẠCH.xlsx> <out.xlsx>
"""
import copy
import datetime as dt
import sys

import openpyxl
from openpyxl.worksheet.pagebreak import Break

REF, TEAM_PLAN, OUT = sys.argv[1:4]
wb = openpyxl.load_workbook(REF)
ws = wb.active
ws.title = "Kế hoạch ĐA127"
team = openpyxl.load_workbook(TEAM_PLAN)["File kế hoạch mẫu"]

ws["A2"] = "KẾ HOẠCH THỰC HIỆN MÔN ĐỒ ÁN CÔNG NGHỆ THÔNG TIN — BÁO CÁO TUẦN 13 (09/11 – 15/11/2026)"
ws["A4"] = "THÔNG TIN SINH VIÊN"
ws["A5"], ws["D5"] = "Sinh viên 1 (nhóm trưởng):", "Phạm Huỳnh Quốc Đạt — MSSV 52300098"
ws["A6"], ws["D6"] = "Sinh viên 2:", "Hoàng Sinh Hùng — MSSV 52300106"
ws["D8"], ws["D9"] = "PGS.TS. Lê Anh Cường", "ĐA127"
ws["D10"] = ("Phát triển hệ thống hỏi đáp pháp luật Việt Nam dựa trên Agentic-RAG với truy xuất căn cứ "
             "theo hiệu lực và kiểm chứng trích dẫn")  # nguyên văn mục 1 đề cương
ws["D11"] = "15/08/2026 (theo đề cương); hạn nộp 23:59 ngày 04/12/2026 (dời từ 21/11)"

LAST_WEEK = 17
# tuần 1–10: nguyên văn kế hoạch nhóm (hàng 16–25 của file nhóm); tuần 11–12: như báo cáo tuần 11–12; tuần 13–17: cập nhật tuần này
plan = {w: (team.cell(15 + w, 4).value, team.cell(15 + w, 5).value or "", team.cell(15 + w, 6).value) for w in range(1, 11)}
for w in (6, 7):  # file mẫu của Khoa đặt mốc giữa kỳ ở tuần 6–7; nhóm báo cáo giữa kỳ thực tế ngày 22/10/2026, tuần 10
    plan[w] = ("Mốc giữa kỳ theo file kế hoạch mẫu của Khoa (nhóm báo cáo giữa kỳ thực tế ngày 22/10/2026, tuần 10)", "", None)
plan[11] = (team.cell(26, 4).value,
            "- Đạt: xong 6/6 task Sprint 4 (API FastAPI, lọc hiệu lực RQ4, pipeline thực nghiệm, bộ chấm Groq; 274 test)\n"
            "- Nạp BLLĐ 2012 vào chỉ mục; kiểm chéo 37 câu manual; tập kiểm thử 179 câu\n"
            "- Chạy và chấm RQ3 (5 cấu hình) và RQ4 (12 câu × 3 chính sách) lần 1\n"
            "- Sửa router từ chối nhầm và bước kiểm chứng gỡ nhầm trích dẫn; đang chạy lại\n"
            "- Hùng: ghép giao diện–API, chấm tay 20 câu, rà soát M_017 (đang thực hiện)", 0.9)
plan[12] = ("- Chạy lại RQ3, RQ4 với bước kiểm chứng đã sửa; chạy lại RQ1, RQ2 (77 câu Zalo)\n"
            "- Đo độ trễ 20 câu không dùng cache; ghép giao diện với API\n"
            "- Chấm tay 20 câu, đo đồng thuận với bộ chấm LLM; đóng băng tính năng (dời sang 12/11 theo hạn mới)",
            "- Chạy lại RQ1–RQ4 sau khi sửa bước kiểm chứng; tập giữ riêng 30 câu chốt trước (209 câu)\n"
            "- Kiểm định bootstrap 95%; phép thử tiêm trích dẫn sai 96/97; chấm tay 20 câu\n"
            "- Đo độ trễ (full 15,9 s), phân tích 20 câu sai, 4 biểu đồ; bản nháp Chương 3–4 (Đạt)\n"
            "- Hùng: giao diện web NiceGUI kết nối API; bản nháp Chương 1; thang chấm; sơ đồ kiến trúc, activity\n"
            "- 319 test; hạn nộp dời 04/12, kế hoạch đã điều chỉnh", 1.0)
plan[13] = ("- Chương 2, Chương 5; cập nhật số liệu Chương 1; sơ đồ use case, sequence\n"
            "- Rà soát Chương 3–4; ĐÓNG BĂNG TÍNH NĂNG 12/11\n- 15/11: nghiệm thu Sprint 5 (bản nháp Chương 1–5)",
            "- Báo cáo đủ 6 chương: thêm Tổng quan tài liệu, viết Kết luận, cập nhật Chương 1 (Đạt làm thay)\n"
            "- Sơ đồ use case, sequence; vẽ lại Hình 4.1–4.2 theo mã nguồn\n"
            "- Ghép báo cáo bằng script theo mẫu môn Dự án của Khoa (~77 trang); rà soát độc lập, sửa hết\n"
            "- Làm sớm Sprint 6 (06/11): Docker, bộ chỉ mục nộp kèm, README tái lập; 381 test\n"
            "- Đánh giá giao diện, vá 2 lỗi sai sự thật; Hùng: nháp Chương 3 (06/11)", 1.0)
plan[14] = ("- Đối chiếu quy định trình bày, rubric của môn\n"
            "- Hình 3.1–3.4, sơ đồ activity (Hùng, hạn 20/11)\n- Chạy thử Docker trên trình duyệt, Windows", "Chưa đến hạn", None)
plan[15] = ("- Rà soát kỹ thuật toàn bộ báo cáo; kiểm tra Turnitin\n"
            "- Slide bảo vệ, video demo 4 kịch bản\n- 27/11: báo cáo hoàn chỉnh", "Chưa đến hạn", None)
plan[16] = ("- 28/11 – 03/12: cập nhật mục lục, ký, xuất PDF; tập dượt bảo vệ\n"
            "- NỘP BÁO CÁO CUỐI KỲ trên ELIT ngày 03/12 (hạn chót 23:59 ngày 04/12/2026)", "Chưa đến hạn", None)
plan[17] = ("TỔ CHỨC PHẢN BIỆN (theo lịch của Khoa)", "Chưa đến hạn", None)

ROW0, NORMAL, MILESTONE, YELLOW_E = 14, 15, 25, 14  # hàng mẫu trong file KLTN
MILESTONES, CURRENT = {10, 16, 17}, 13


styles = {r: [copy.copy(ws.cell(r, c)._style) for c in range(1, 7)] for r in (NORMAL, MILESTONE, YELLOW_E)}
for w in range(1, LAST_WEEK + 1):
    r = ROW0 + w - 1
    proto = MILESTONE if w in MILESTONES else NORMAL
    for c in range(1, 7):
        ws.cell(r, c)._style = copy.copy(styles[proto][c - 1])
    if w == CURRENT:
        for c in (5, 6):
            ws.cell(r, c)._style = copy.copy(styles[YELLOW_E][c - 1])
    todo, done, pct = plan[w]
    ws.cell(r, 1).value = w
    ws.cell(r, 2).value = dt.datetime(2026, 8, 15) if w == 1 else f"=C{r - 1}+1"
    # tuần 1 từ thứ Bảy 15/08 (theo đề cương) đến hết Chủ nhật 23/08; các tuần sau thứ Hai – Chủ nhật
    ws.cell(r, 3).value = f"=B{r}+8" if w == 1 else f"=B{r}+6"
    ws.cell(r, 4).value = todo
    ws.cell(r, 5).value = done
    if isinstance(pct, str):  # file nhóm ghi "100%" / "~70%" dạng chữ
        pct = 0.7 if "70" in pct else float(pct.strip("%")) / 100
    ws.cell(r, 6).value = pct  # .value: cell(r, c, None) không ghi đè giá trị cũ của file mẫu
    wrapped = lambda s, width: sum(-(-len(line) // width) or 1 for line in str(s or "").split("\n"))
    ws.row_dimensions[r].height = max(34, 16.5 * max(wrapped(todo, 40 if w in MILESTONES else 46), wrapped(done, 50)) + 8)  # chữ đậm ở hàng mốc chiếm rộng hơn; 46 ký tự/dòng đo trên bản render tuần 12

# bỏ hàng của tuần 18–25 và mốc 2027 trong file KLTN (hàng 31–41), dời khối ghi chú + chữ ký lên
FIRST_DEL = ROW0 + LAST_WEEK            # 31
N_DEL = 42 - FIRST_DEL                  # hàng 31–41
for rng in ["B39:C39", "B40:C40", "B41:C41", "D39:F39", "D40:F40", "D41:F41", "E46:F46", "E47:F47", "E51:F51"]:
    ws.unmerge_cells(rng)
ws.delete_rows(FIRST_DEL, N_DEL)
for row in (46, 47, 51):
    ws.merge_cells(f"E{row - N_DEL}:F{row - N_DEL}")
heights = {r: ws.row_dimensions[r + N_DEL].height for r in range(FIRST_DEL, FIRST_DEL + 11)}
for r, h in heights.items():
    ws.row_dimensions[r].height = h
NOTE = 43 - N_DEL                       # hàng "Ghi chú" của file KLTN sau khi dời
ws[f"A{NOTE}"] = "Ghi chú:"
ws[f"B{NOTE}"] = ("Dòng nền xanh: mốc của Khoa/đề tài. Ô nền vàng: tuần đang báo cáo (tuần 13). Tuần 1–10 theo kế hoạch nhóm "
                  "đã nộp; tuần 11–12 như báo cáo tuần 11–12.")
ws[f"B{NOTE + 1}"] = ("% hoàn thành tuần 13 = 100%: mọi việc dự kiến của tuần đã xong (Đạt làm thay phần của Hùng), thêm phần "
                      "đóng gói và ghép báo cáo của Sprint 6 làm sớm. Tác tử, prompt, tập kiểm thử không đổi.")
ws[f"E{51 - N_DEL}"] = "PGS.TS. Lê Anh Cường"
# ngắt trang trước tuần đang báo cáo: tuần 13–17, ghi chú và chữ ký in chung một trang
ws.row_breaks.append(Break(id=ROW0 + CURRENT - 2))
# bảng dài hơn tuần 11 (17 tuần): lề trên/dưới 1" → 0,6" để tên GVHD không tràn sang trang mới
ws.page_margins.top = ws.page_margins.bottom = 0.6
ws.page_margins.header = ws.page_margins.footer = 0.3
wb.calculation.fullCalcOnLoad = True  # openpyxl không lưu giá trị công thức: để Excel tính lại khi mở
wb.properties.title = "Kế hoạch ĐA127 — báo cáo tuần 13"
wb.save(OUT)
print("saved", OUT)
