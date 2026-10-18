"""Tách toàn văn Điều thành dẫn nhập + từng Khoản để tô sáng Khoản được trích."""
import re

_CLAUSE_RE = re.compile(r"(\d+)\. ")


def article_key(chunk_id):
    """BLDS2015_Dieu357_Khoan1 -> BLDS2015_Dieu357."""
    return re.sub(r"_Khoan\w+$", "", chunk_id)


def split_clauses(content):
    """[(số Khoản hoặc None cho dẫn nhập, đoạn văn)]; các Điểm a), b)... nằm trong Khoản của chúng."""
    blocks = []
    for line in content.split("\n"):
        m = _CLAUSE_RE.match(line)
        if m or not blocks:
            blocks.append((m.group(1) if m else None, [line]))
        else:
            blocks[-1][1].append(line)
    return [(number, "\n".join(lines)) for number, lines in blocks]


def clause_number(clause):
    """'Khoản 2' -> '2'; None nếu trích dẫn cấp Điều."""
    return clause.removeprefix("Khoản ").strip() if clause else None
