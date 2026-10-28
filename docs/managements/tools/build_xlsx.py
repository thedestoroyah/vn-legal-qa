"""Kế hoạch tuần .xlsx: khuôn file KLTN (định dạng), nội dung tuần 1–10 lấy nguyên văn từ KẾ HOẠCH.xlsx của nhóm."""
import copy
import datetime as dt
import sys

import openpyxl

REF, TEAM_PLAN, OUT = sys.argv[1:4]
wb = openpyxl.load_workbook(REF)
ws = wb.active
ws.title = "Kế hoạch ĐA127"
team = openpyxl.load_workbook(TEAM_PLAN)["File kế hoạch mẫu"]

ws["A2"] = "KẾ HOẠCH THỰC HIỆN MÔN ĐỒ ÁN CÔNG NGHỆ THÔNG TIN — BÁO CÁO TUẦN 11 (26/10 – 01/11/2026)"
ws["A4"] = "THÔNG TIN SINH VIÊN"
ws["A5"], ws["D5"] = "Sinh viên 1 (nhóm trưởng):", "Phạm Huỳnh Quốc Đạt — MSSV 52300098"
ws["A6"], ws["D6"] = "Sinh viên 2:", "Hoàng Sinh Hùng — MSSV 52300106"
ws["D8"], ws["D9"] = "PGS.TS. Lê Anh Cường", "ĐA127"
ws["D10"] = ("Phát triển hệ thống hỏi đáp pháp luật Việt Nam dựa trên Agentic-RAG với truy xuất căn cứ "
             "theo hiệu lực và kiểm chứng trích dẫn")  # nguyên văn mục 1 đề cương
ws["D11"] = "15/08/2026 (theo đề cương); hạn nộp 23:59 ngày 21/11/2026"

# tuần 1–10: nguyên văn kế hoạch nhóm (hàng 16–25 của file nhóm); tuần 11–15: cập nhật tuần này
plan = {w: (team.cell(15 + w, 4).value, team.cell(15 + w, 5).value or "", team.cell(15 + w, 6).value) for w in range(1, 11)}
for w in (6, 7):  # file mẫu của Khoa đặt mốc giữa kỳ ở tuần 6–7; nhóm báo cáo giữa kỳ thực tế ngày 22/10 (tuần 10)
    plan[w] = ("Mốc giữa kỳ theo file kế hoạch mẫu của Khoa (nhóm báo cáo giữa kỳ thực tế ngày 22/10/2026, tuần 10)", "", None)
plan[11] = (team.cell(26, 4).value,
            "- Đạt: xong 6/6 task Sprint 4 (API FastAPI, lọc hiệu lực RQ4, pipeline thực nghiệm, bộ chấm Groq; 274 test)\n"
            "- Nạp BLLĐ 2012 vào chỉ mục; kiểm chéo 37 câu manual; tập kiểm thử 179 câu\n"
            "- Chạy và chấm RQ3 (5 cấu hình) và RQ4 (12 câu × 3 chính sách) lần 1\n"
            "- Sửa router từ chối nhầm và bước kiểm chứng gỡ nhầm trích dẫn; đang chạy lại\n"
            "- Hùng: ghép giao diện–API, chấm tay 20 câu, rà soát M_017 (đang thực hiện)", 0.9)
plan[12] = ("- Chạy lại RQ3, RQ4 với bước kiểm chứng đã sửa; chạy lại RQ1, RQ2 (77 câu Zalo)\n"
            "- Đo độ trễ 20 câu không dùng cache; ghép giao diện với API\n"
            "- Chấm tay 20 câu, đo đồng thuận với bộ chấm LLM; ĐÓNG BĂNG TÍNH NĂNG 08/11", "Chưa đến hạn", None)
plan[13] = ("- Bảng tổng hợp, biểu đồ RQ1–RQ4; phân tích 20 trường hợp sai\n"
            "- Viết Chương 1–4; sơ đồ use case, activity, sequence\n- Docker và docker-compose", "Chưa đến hạn", None)
plan[14] = ("- Chương 5; rà soát kỹ thuật; kiểm tra Turnitin; slide và video demo\n"
            "- 18/11: báo cáo hoàn chỉnh gửi GVHD duyệt\n- NỘP BÁO CÁO CUỐI KỲ trước 23:59 ngày 21/11/2026", "Chưa đến hạn", None)
plan[15] = ("TỔ CHỨC PHẢN BIỆN (theo lịch của Khoa)", "Chưa đến hạn", None)

ROW0, NORMAL, MILESTONE, YELLOW_E = 14, 15, 25, 14  # hàng mẫu trong file KLTN
MILESTONES, CURRENT = {10, 14, 15}, 11


def copy_style(src, dst):
    dst.font, dst.fill, dst.border = copy.copy(src.font), copy.copy(src.fill), copy.copy(src.border)
    dst.alignment, dst.number_format = copy.copy(src.alignment), src.number_format


styles = {r: [copy.copy(ws.cell(r, c)._style) for c in range(1, 7)] for r in (NORMAL, MILESTONE, YELLOW_E)}
for w in range(1, 16):
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
    ws.row_dimensions[r].height = max(34, 16.5 * max(wrapped(todo, 44 if w in MILESTONES else 52), wrapped(done, 52)) + 8)  # chữ đậm ở hàng mốc chiếm rộng hơn

# bỏ hàng 29–41 của file KLTN (tuần 16–25 và mốc 2027), dời khối ghi chú + chữ ký lên
for rng in ["B39:C39", "B40:C40", "B41:C41", "D39:F39", "D40:F40", "D41:F41", "E46:F46", "E47:F47", "E51:F51"]:
    ws.unmerge_cells(rng)
ws.delete_rows(29, 13)
for rng in ["E33:F33", "E34:F34", "E38:F38"]:
    ws.merge_cells(rng)
heights = {r: ws.row_dimensions[r + 13].height for r in range(29, 40)}
for r, h in heights.items():
    ws.row_dimensions[r].height = h
ws["A30"] = "Ghi chú:"
ws["B30"] = "Dòng nền xanh: mốc của Khoa/đề tài. Ô nền vàng: tuần đang báo cáo (tuần 11). Tuần 1–10 theo kế hoạch nhóm đã nộp."
ws["B31"] = ("% hoàn thành tuần 11 = 90%: phần kỹ thuật Sprint 4 xong; còn chạy lại RQ3/RQ4 sau khi sửa bước kiểm chứng "
             "(chờ hạn mức API) và phần ghép giao diện, chấm tay của Hùng.")
ws["E38"] = "PGS.TS. Lê Anh Cường"
wb.calculation.fullCalcOnLoad = True  # openpyxl không lưu giá trị công thức: để Excel tính lại khi mở
wb.properties.title = "Kế hoạch ĐA127 — báo cáo tuần 11"
wb.save(OUT)
print("saved", OUT)
