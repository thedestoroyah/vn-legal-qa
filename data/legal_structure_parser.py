from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

# Markdown/layout
HEADING_RE = re.compile(r"^\s*#{1,6}\s*")
BOLD_RE = re.compile(r"^\s*\*\*(.*?)\*\*\s*$")
ESCAPED_BOLD_RE = re.compile(r"^\s*\\\*\\\*(.*?)\\\*\\\*\s*$")
ANCHOR_RE = re.compile(r"^\s*<a\b[^>]*>\s*</a>\s*$", re.I)
PAGE_RE = re.compile(r"^\s*<!--\s*page\s+\d+(?:\s+of\s+\d+)?\s*-->\s*$", re.I)
DECORATION_RE = re.compile(r"^[\\_\-=*.\s]{3,}$")


# Legal hierarchy
PART_RE = re.compile(r"^Phần\s+(.+)$", re.I)
CHAPTER_RE = re.compile(r"^Chương\s+([IVXLCDM]+|\d+)$", re.I)
# SECTION_RE = re.compile(r"^(Mục|Tiểu mục)\s+(.+)$", re.I)
SECTION_RE = re.compile(r"^(Mục|Tiểu mục)\s+([IVXLCDM]+|\d+[a-zđ]?)\b\.?\s*(.*)$", re.I)
ARTICLE_RE = re.compile(r"^Điều\s+(\d+)\.\s*(.*?)$", re.I)
CLAUSE_RE = re.compile(r"^(\d+)\.\s+(.+)$")
POINT_RE = re.compile(r"^([a-zA-ZđĐ])\)\s*(.+)$")
LAW_NUMBER_RE = re.compile(
    r"(?:(?:Bộ\s+)?Luật\s+số|Số)\s*:\s*([0-9]+/[0-9]+/[A-ZĐa-zđ]+[0-9]*)",
    re.I,
)
# Quote handling (curly quotes are used in legal documents)
QUOTE_OPEN_CHAR = "“"
QUOTE_CLOSE_CHAR = "”"


@dataclass
class Point:
    type: str = "point"
    number: str = ""
    text: str = ""


@dataclass
class Clause:
    type: str = "clause"
    number: str = ""
    text: str = ""
    points: list[Point] = field(default_factory=list)


@dataclass
class Article:
    type: str = "article"
    number: str = ""
    title: str = ""
    text: str = ""
    clauses: list[Clause] = field(default_factory=list)


@dataclass
class Section:
    type: str = "section"
    number: str = ""
    title: str = ""
    articles: list[Article] = field(default_factory=list)


@dataclass
class Chapter:
    type: str = "chapter"
    number: str = ""
    title: str = ""
    sections: list[Section] = field(default_factory=list)
    articles: list[Article] = field(default_factory=list)


@dataclass
class Part:
    type: str = "part"
    number: str = ""
    title: str = ""
    chapters: list[Chapter] = field(default_factory=list)
    articles: list[Article] = field(default_factory=list)


@dataclass
class Law:
    type: str = "law"
    name: str = ""
    law_number: Optional[str] = None
    source_file: str = ""
    parts: list[Part] = field(default_factory=list)
    chapters: list[Chapter] = field(default_factory=list)
    articles: list[Article] = field(default_factory=list)


def strip_markup(line: str) -> str:
    """Remove presentation syntax only; do not alter legal numbers/text."""
    line = HEADING_RE.sub("", line.strip()).strip()
    # Loại bỏ mọi dấu bold, kể cả bold một phần như **Điều 1.**
    line = line.replace("**", "").replace("__", "")
    # m = BOLD_RE.match(line) or ESCAPED_BOLD_RE.match(line)
    # if m:
    #     line = m.group(1)
    # line = line.replace(r"\*\*", "**")
    # if line.startswith("**") and line.endswith("**"):
    #     line = line[2:-2]
    return re.sub(r"\s+", " ", line).strip()


def is_layout(line: str) -> bool:
    s = line.strip()
    return not s or PAGE_RE.match(s) is not None or ANCHOR_RE.match(s) is not None or DECORATION_RE.match(s) is not None


def is_html_table(line: str) -> bool:
    s = line.strip().lower()
    return any(x in s for x in ("<table", "</table>", "<tr", "</tr", "<td", "</td"))


def join_text(old: str, new: str) -> str:
    return new if not old else f"{old} {new}"


class LegalStructureParser:
    """Parser for normalized MinerU Markdown of Vietnamese legislation.

    Hỗ trợ:
    - Bold/italic một phần (ví dụ ``**Điều 1.** Phạm vi điều chỉnh``).
    - Điều lồng điều (ví dụ Điều 219 sửa đổi Điều 54, 55, 73 của luật khác):
      nội dung bên trong cặp dấu ngoặc kép ``“...“`` được giữ nguyên dưới
      dạng text của point hiện hành, không bị nhận diện nhầm thành
      clause/point/article mới.
    - Cắt phần chữ ký cuối văn bản (``Bộ luật này ... được Quốc hội ...``).
    """

    MAX_DEPTH = 20

    def __init__(self, source_file: str = ""):
        self.law = Law(source_file=source_file)
        self.current_part: Optional[Part] = None
        self.current_chapter: Optional[Chapter] = None
        self.current_section: Optional[Section] = None
        self.current_article: Optional[Article] = None
        self.current_clause: Optional[Clause] = None
        self.current_point: Optional[Point] = None
        self.pending_chapter_title = False
        self.pending_section_title = False
        self.pending_law_name = False
        self.in_quote = False

    def parse_file(self, path: Path) -> Law:
        self.law.source_file = path.name
        return self.parse_text(path.read_text(encoding="utf-8"))

    def parse_text(self, text: str) -> Law:
        for raw in text.splitlines():
            self.parse_line(raw)
        return self.law

    def parse_line(self, raw: str,  _depth: int = 0) -> None:
        if _depth > self.MAX_DEPTH:
            return
        
        if is_layout(raw):
            return

        if is_html_table(raw):
            self._extract_metadata(re.sub(r"<[^>]+>", " ", raw))
            return

        line = strip_markup(raw)
        if not line:
            return

        self._extract_metadata(line)

         # 1. Đang trong đoạn trích dẫn → chỉ nối text, không nhận diện cấu trúc
        if self.in_quote:
            self._handle_in_quote(line, _depth)
            return

        # 2. Phát hiện mở trích dẫn trong dòng
        qi = line.find(QUOTE_OPEN_CHAR)
        if qi != -1:
            before = line[:qi].strip()
            after = line[qi:]
            if before:
                self.parse_line(before, _depth + 1)
            self.in_quote = True
            self._handle_in_quote(after, _depth + 1)
            return

        # 3. Xử lý bình thường
        m = PART_RE.match(line)
        if m:
            self._start_part(m.group(1).strip())
            return

        m = CHAPTER_RE.match(line)
        if m:
            self._start_chapter(m.group(1).strip())
            return

        m = SECTION_RE.match(line)
        if m:
            self._start_section(m.group(1), m.group(2).strip())
            return

        m = ARTICLE_RE.match(line)
        if m:
            self._start_article(m.group(1), m.group(2).strip())
            return

        # Clause numbering is meaningful only inside an Article.
        m = CLAUSE_RE.match(line)
        if m and self.current_article is not None:
            self._start_clause(m.group(1), m.group(2).strip())
            return

        # Point lettering is meaningful only inside a Clause.
        m = POINT_RE.match(line)
        if m and self.current_clause is not None:
            self._start_point(m.group(1), m.group(2).strip())
            return

        # Chapter/section title is the standalone line immediately after it.
        if self.pending_chapter_title and self.current_chapter:
            self.current_chapter.title = line
            self.pending_chapter_title = False
            return

        if self.pending_section_title and self.current_section:
            self.current_section.title = line
            self.pending_section_title = False
            return

        self._append_text(line)

    # Quote handling
    def _handle_in_quote(self, line: str, _depth: int = 0) -> None:
        if _depth > self.MAX_DEPTH:
            self._append_text(line)
            return

        ci = line.find(QUOTE_CLOSE_CHAR)
        if ci == -1:
            self._append_text(line)
            return

        before = line[: ci + 1]          # bao gồm cả dấu đóng
        after = line[ci + 1 :].strip()   # phần sau dấu đóng

        self._append_text(before)
        self.in_quote = False

        if after:
            self.parse_line(after, _depth + 1)

    # Context resets
    def _close_article_context(self) -> None:
        self.current_article = None
        self.current_clause = None
        self.current_point = None

    # Structure starters
    def _start_part(self, number: str) -> None:
        self._close_article_context()
        p = Part(number=number)
        self.law.parts.append(p)
        self.current_part = p
        self.current_chapter = None
        self.current_section = None
        self.pending_chapter_title = False
        self.pending_section_title = False

    def _start_chapter(self, number: str) -> None:
        self._close_article_context()
        c = Chapter(number=number)
        if self.current_part:
            self.current_part.chapters.append(c)
        else:
            self.law.chapters.append(c)
        self.current_chapter = c
        self.current_section = None
        self.pending_chapter_title = True
        self.pending_section_title = False

    def _start_section(self, kind: str, number: str) -> None:
        self._close_article_context()
        if not self.current_chapter:
            raise ValueError(f"{self.law.source_file}: {kind} {number} without a chapter")
        s = Section(number=number, title=kind)
        self.current_chapter.sections.append(s)
        self.current_section = s
        self.pending_section_title = True
        self.pending_chapter_title = False

    def _start_article(self, number: str, title: str) -> None:
        self._close_article_context()
        a = Article(number=number, title=title)
        if self.current_section:
            self.current_section.articles.append(a)
        elif self.current_chapter:
            self.current_chapter.articles.append(a)
        elif self.current_part:
            self.current_part.articles.append(a)
        else:
            self.law.articles.append(a)
        self.current_article = a
        self.current_clause = None
        self.current_point = None
        self.pending_chapter_title = False
        self.pending_section_title = False

    def _start_clause(self, number: str, text: str) -> None:
        c = Clause(number=number, text=text)
        self.current_article.clauses.append(c)
        self.current_clause = c
        self.current_point = None

    def _start_point(self, number: str, text: str) -> None:
        p = Point(number=number, text=text)
        self.current_clause.points.append(p)
        self.current_point = p

    def _append_text(self, line: str) -> None:

        if self.pending_law_name:
            self.law.name = join_text(self.law.name, line) if self.law.name else line
            self.pending_law_name = False
            return
        if self.current_point:
            self.current_point.text = join_text(self.current_point.text, line)
        elif self.current_clause:
            self.current_clause.text = join_text(self.current_clause.text, line)
        elif self.current_article:
            self.current_article.text = join_text(self.current_article.text, line)
        elif line.upper() in {"LUẬT", "BỘ LUẬT"}:
            self.law.name = line
            self.pending_law_name = True

    def _extract_metadata(self, line: str) -> None:
        if not self.law.law_number:
            m = LAW_NUMBER_RE.search(line)
            if m:
                self.law.law_number = m.group(1)

# Helpers
def count_articles(law: Law) -> int:
    total = len(law.articles)
    for p in law.parts:
        total += len(p.articles)
        for c in p.chapters:
            total += len(c.articles)
            total += sum(len(s.articles) for s in c.sections)
    for c in law.chapters:
        total += len(c.articles)
        total += sum(len(s.articles) for s in c.sections)
    return total


def save(law: Law, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(law), ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=Path("structured"))
    args = ap.parse_args()

    files = [args.input] if args.input.is_file() else sorted(args.input.glob("*.md"))
    if not files:
        raise SystemExit(f"No Markdown files found: {args.input}")

    for src in files:
        parser = LegalStructureParser(src.name)
        law = parser.parse_file(src)
        dst = args.output if args.output.suffix == ".json" else args.output / f"{src.stem}.json"
        save(law, dst)
        print(f"[OK] {src.name} -> {dst}")
        print(f"     law_number={law.law_number}, parts={len(law.parts)}, chapters={len(law.chapters)}, articles={count_articles(law)}")


if __name__ == "__main__":
    main()
  