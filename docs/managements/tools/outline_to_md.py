"""Chuyển 'Đề cương DACNTT.txt' (xuất từ Google Docs, thụt lề vô nghĩa) sang Markdown theo nội dung từng dòng."""
import re
import sys

src, dst = sys.argv[1:3]
lines = open(src, encoding="utf-8-sig").read().splitlines()
last_section = -1  # tiêu đề chương phải tăng đúng 1: "1. Xây dựng..." trong 3.2 là mục liệt kê, không phải chương
out, in_json, depth_open = [], 0, False
SECTION = re.compile(r"^(\d{1,2})\.\s+(.+)$")
SUB = re.compile(r"^(\d{1,2}\.\d)\.\s+(.+)$")
LABELS = re.compile(r"^(Phạm Huỳnh Quốc Đạt|Hoàng Sinh Hùng|Cả hai|Mục tiêu sprint|Nghiệm thu sprint|Phương án dự phòng|"
                    r"Khoảng trống nghiên cứu|Yêu cầu|Phản hồi)\b")


def blank():
    if out and out[-1] != "":
        out.append("")


for i, raw in enumerate(lines):
    s = raw.strip()
    if in_json:  # khối JSON của Phụ lục A
        out.append(raw.rstrip())
        in_json += s.count("{") - s.count("}")
        if in_json == 0:
            out.append("```")
            blank()
        continue
    if s == "{":
        blank()
        out += ["```json", "{"]
        in_json = 1
        continue
    if not s:
        depth_open = False
        blank()
        continue
    if i == 0:
        out += [f"# {s}", ""]
        continue
    if i == 1:
        out += [f"**{s}**", ""]
        continue
    if set(s) == {"_"}:
        blank(); out += ["---", ""]; continue
    col0 = not raw[:1].isspace()
    if s.startswith(("PHỤ LỤC", "SPRINT ")) and col0:
        blank(); out += [("## " if s.startswith("PHỤ LỤC") else "### ") + s, ""]; continue
    if re.match(r"^A\.\d\.", s):
        blank(); out += [f"### {s}", ""]; continue
    if re.match(r"^(Sprint \d|Giai đoạn \d)", s) and col0:
        blank(); out += [f"### {s}", ""]; depth_open = False; continue
    m = SUB.match(s)
    if m and col0:
        blank(); out += [f"### {m.group(1)}. {m.group(2)}", ""]; depth_open = False; continue
    m = SECTION.match(s)
    if m and col0 and (s.endswith(":") or len(s) < 60) and int(m.group(1)) == last_section + 1:
        last_section = int(m.group(1))
        blank(); out += [f"## {m.group(1)}. {m.group(2).rstrip(':').strip()}", ""]; depth_open = False; continue
    if s.startswith("* "):
        text = s[2:].strip()
        label = text.endswith(":") and len(text) < 110
        if label:
            out.append(f"- **{text}**")
            depth_open = True
        else:
            out.append(("  - " if depth_open else "- ") + text)
        continue
    m = re.match(r"^\[( |x)\]\s*(.+)$", s)
    if m:
        out.append(f"- [{m.group(1)}] {m.group(2)}")
        continue
    m = re.match(r"^(\d{1,2})\.\s+(.+)$", s)  # mục liệt kê có số (không phải tiêu đề)
    if m:
        text = m.group(2)
        if text.endswith(":") and len(text) < 110:
            out.append(f"{m.group(1)}. **{text}**")
            depth_open = True
        else:
            out.append(f"{m.group(1)}. {text}")
            depth_open = False
        continue
    if LABELS.match(s) and s.endswith(":"):  # nhãn cả dòng, vd "Phạm Huỳnh Quốc Đạt (chi tiết: ...):"
        blank(); out += [f"**{s}**", ""]
        continue
    if LABELS.match(s):
        label, _, rest = s.partition(": ")
        blank(); out += [f"**{label}:**{(' ' + rest.strip()) if rest.strip() else ''}", ""]
        continue
    if out and out[-1].startswith("## 12."):  # tài liệu tham khảo: mỗi dòng một mục
        pass
    if any(o.startswith("## 12.") for o in out) and not any(o.startswith("## PHỤ LỤC") for o in out):
        out.append(f"- {s}")
        continue
    blank(); out += [s, ""]

text = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"
open(dst, "w", encoding="utf-8").write(text)
print("lines", len(text.splitlines()))
