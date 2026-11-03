"""Dựng báo cáo tuần .docx từ file mẫu KLTN: giữ trang bìa, style, lề, header/footer; thay nội dung bằng content.json."""
import copy
import json
import re
import sys

import docx
from docx.oxml.ns import qn

REF, OUT, CONTENT = sys.argv[1:4]
C = json.load(open(CONTENT, encoding="utf-8"))
M = C["meta"]
d = docx.Document(REF)
body = d.element.body
els = list(body)
P = lambda i: els[i]

# đoạn mẫu (chỉ số theo cấu trúc file mẫu đã khảo sát)
H1, H2, BODY, BULLET, CAPTION, TABLE, AFTER_TBL = (copy.deepcopy(P(i)) for i in (39, 40, 41, 45, 50, 51, 52))
SIGN_DATE, SIGN_TBL = copy.deepcopy(els[-3]), copy.deepcopy(els[-2])
sect = els[-1]


def set_runs(p, parts):
    """Ghi lại các run của đoạn: parts = [(text, bold)]; giữ rPr của run mẫu tương ứng (run đậm/run thường)."""
    runs = p.findall(qn("w:r"))
    proto_bold = next((r for r in runs if r.find(".//" + qn("w:b")) is not None), runs[0])
    proto_norm = next((r for r in runs if r.find(".//" + qn("w:b")) is None), runs[-1])
    for r in runs:
        p.remove(r)
    for text, bold in parts:
        r = copy.deepcopy(proto_bold if bold else proto_norm)
        for t in r.findall(qn("w:t")):
            r.remove(t)
        for extra in r.findall(qn("w:br")):
            r.remove(extra)
        t = r.makeelement(qn("w:t"), {qn("xml:space"): "preserve"})
        t.text = text
        r.append(t)
        p.append(r)
    return p


def para(proto, parts):
    return set_runs(copy.deepcopy(proto), parts if isinstance(parts, list) else [(parts, False)])


def norm_body():
    """Đoạn thân bài: run mẫu của BODY không đậm."""
    return BODY


def table(head, rows, widths=None):
    """Bảng theo mẫu: hàng tiêu đề nền xanh d9e2f3, chữ 13pt; số cột tùy ý."""
    t = copy.deepcopy(TABLE)
    trs = t.findall(qn("w:tr"))
    head_tr, data_tr = trs[0], trs[1]
    for tr in trs:
        t.remove(tr)
    n = len(head)
    total = 9000
    widths = widths or [total // n] * n
    grid = t.find(qn("w:tblGrid"))
    for g in grid.findall(qn("w:gridCol")):
        grid.remove(g)
    for w in widths:
        grid.append(grid.makeelement(qn("w:gridCol"), {qn("w:w"): str(w)}))

    def make_row(proto_tr, cells, bold):
        tr = copy.deepcopy(proto_tr)
        tcs = tr.findall(qn("w:tc"))
        proto_tc = tcs[0] if bold else tcs[-1]
        for tc in tcs:
            tr.remove(tc)
        for i, text in enumerate(cells):
            tc = copy.deepcopy(proto_tc)
            tc.find(qn("w:tcPr")).find(qn("w:tcW")).set(qn("w:w"), str(widths[i]))
            p = tc.find(qn("w:p"))
            for extra in tc.findall(qn("w:p"))[1:]:
                tc.remove(extra)
            lines = text.split("\n")
            for j, line in enumerate(lines):
                q = p if j == 0 else copy.deepcopy(p)
                set_runs(q, [(("• " if len(lines) > 1 else "") + line, bold)])
                jc = q.find(qn("w:pPr")).find(qn("w:jc"))
                if jc is not None:
                    jc.set(qn("w:val"), "center" if bold or i > 0 and len(text) < 14 else "left")
                if j:
                    tc.append(q)
            tr.append(tc)
        return tr

    t.append(make_row(head_tr, head, True))
    for r in rows:
        t.append(make_row(data_tr, r, False))
    return t


# ---- trang bìa: sửa chữ ở 2 trang bìa (chỉ số 0–38), xóa phần thân cũ
def cover_text(i, text):
    p = docx.text.paragraph.Paragraph(P(i), d)
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]:
        r.text = ""


for base in (0, 19):
    k = 8 if base == 0 else 27
    cover_text(k, " | ".join(M["students"]).replace(" | ", "\n"))
    cover_text(k + 2, M["title"])
    cover_text(k + 4, f"{M['report']}\n{M['course']}")
    cover_text(k + 6, M["week"].upper())
# trang bìa trong: dòng "Người hướng dẫn" giữ nguyên, tên GVHD giữ nguyên
for el in els[39:-1]:  # giữ sectPr (lề, header/footer)
    body.remove(el)

out = []
ch1 = C["ch1"]
out.append(para(H1, ch1["title"]))
out.append(para(BODY, ch1["intro"]))
for s in ch1["sections"]:
    out.append(para(H2, s["h"]))
    if s.get("text"):
        out.append(para(BODY, s["text"]))
    for label, text in s.get("items", []):
        out.append(para(BULLET, [(label + ": ", True), (text, False)]))
    if s.get("table"):
        tb = s["table"]
        out.append(para(CAPTION, [(tb["caption"].split(". ", 1)[0] + ". ", True), (tb["caption"].split(". ", 1)[1], False)]))
        n = len(tb["head"])
        widths = [2000] + [7000 // (n - 1)] * (n - 1) if n > 4 else [3400] + [5600 // (n - 1)] * (n - 1)
        out.append(table(tb["head"], tb["rows"], widths))
        out.append(copy.deepcopy(AFTER_TBL))
    if s.get("after"):
        out.append(para(BODY, s["after"]))

ch2 = C["ch2"]
out.append(para(H1, ch2["title"]))
out.append(para(BODY, ch2["intro"]))
tb = ch2["table"]
out.append(para(CAPTION, [(tb["caption"].split(". ", 1)[0] + ". ", True), (tb["caption"].split(". ", 1)[1], False)]))
out.append(table(tb["head"], tb["rows"], [1200, 4600, 3200]))
out.append(copy.deepcopy(AFTER_TBL))
for label, text in ch2["verdict"]:
    out.append(para(BULLET, [(label + ": ", True), (text, False)]))

ch3 = C["ch3"]
out.append(para(H1, ch3["title"]))
out.append(para(BODY, ch3["intro"]))
out.append(para(CAPTION, [("Bảng 3.1. ", True), ("Kế hoạch các tuần còn lại", False)]))
out.append(table(["Tuần", "Thời gian", "Mục tiêu", "Công việc chính"],
                 [[w["name"], w["dates"], w["goal"], "\n".join(w["items"])] for w in ch3["weeks"]],
                 [1000, 1700, 1800, 4500]))
out.append(copy.deepcopy(AFTER_TBL))
out.append(para(BODY, ch3["after"]))

ch4 = C["ch4"]
out.append(para(H1, ch4["title"]))
out.append(para(CAPTION, [("Bảng 4.1. ", True), ("Khó khăn, rủi ro và giải pháp", False)]))
out.append(table(["Khó khăn / rủi ro", "Giải pháp"], ch4["rows"], [3600, 5400]))
out.append(copy.deepcopy(AFTER_TBL))
if ch4.get("resolved"):  # khó khăn tuần trước đã xử lý xong (từ tuần 12)
    out.append(para(BODY, "Các khó khăn đã được xử lý trong tuần:"))
    for label, text in ch4["resolved"]:
        out.append(para(BULLET, [(label + ": ", True), (text, False)]))
date = copy.deepcopy(SIGN_DATE)
dd, mm, yyyy = M["date"].split("/")
out.append(set_runs(date, [(f"TP. Hồ Chí Minh, ngày {int(dd)} tháng {int(mm)} năm {yyyy}", False)]) if date.findall(qn("w:r")) else date)
sign = copy.deepcopy(SIGN_TBL)
out.append(sign)
for el in out:
    sect.addprevious(el)
d.core_properties.title = f"{M['report']} — {M['code']}"
d.core_properties.author = "Phạm Huỳnh Quốc Đạt, Hoàng Sinh Hùng"
d.save(OUT)

# chữ ký: thêm tên SV thứ hai (mẫu KLTN chỉ có 1 SV)
d2 = docx.Document(OUT)
t = d2.tables[-1]
cell = t.rows[0].cells[1]
txt = cell.text
if "Hùng" not in txt:
    last = cell.paragraphs[-1]
    last.runs[0].text = "Phạm Huỳnh Quốc Đạt" if last.runs else ""
    for r in last.runs[1:]:
        r.text = ""
    newp = copy.deepcopy(last._p)
    last._p.addnext(newp)
    np_ = docx.text.paragraph.Paragraph(newp, cell)
    np_.runs[0].text = "Hoàng Sinh Hùng"
d2.save(OUT)
print("saved", OUT)
