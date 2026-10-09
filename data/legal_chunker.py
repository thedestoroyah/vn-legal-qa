from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterator, Optional

from legal_structure_parser import (
    Law, Part, Chapter, Section, Article, Clause, Point,
)


# ============================================================
# 1. Chunk dataclass
# ============================================================
@dataclass
class Chunk:
    chunk_id: str
    law_name: str
    law_number: str
    source_file: str

    part_number: str = ""
    part_title: str = ""

    chapter_number: str = ""
    chapter_title: str = ""

    section_number: str = ""
    section_title: str = ""

    article_number: str = ""
    article_title: str = ""
    clause_number: str = ""        # "" khi chunk theo Điều

    chunk_level: str = "article"   # "article" | "clause"
    text: str = ""
    contextualized_text: str = ""
    char_count: int = 0
    token_estimate: int = 0


# ============================================================
# 2. Deserialize JSON -> dataclass (khớp schema parser)
# ============================================================
def _point(d: dict) -> Point:
    return Point(
        type=d.get("type", "point"),
        number=d.get("number", ""),
        text=d.get("text", ""),
    )


def _clause(d: dict) -> Clause:
    return Clause(
        type=d.get("type", "clause"),
        number=d.get("number", ""),
        text=d.get("text", ""),
        points=[_point(p) for p in d.get("points", [])],
    )


def _article(d: dict) -> Article:
    return Article(
        type=d.get("type", "article"),
        number=d.get("number", ""),
        title=d.get("title", ""),
        text=d.get("text", ""),
        clauses=[_clause(c) for c in d.get("clauses", [])],
    )


def _section(d: dict) -> Section:
    # Section trong parser CHỈ có: type, number, title, articles
    return Section(
        type=d.get("type", "section"),
        number=d.get("number", ""),
        title=d.get("title", ""),
        articles=[_article(a) for a in d.get("articles", [])],
    )


def _chapter(d: dict) -> Chapter:
    return Chapter(
        type=d.get("type", "chapter"),
        number=d.get("number", ""),
        title=d.get("title", ""),
        sections=[_section(s) for s in d.get("sections", [])],
        articles=[_article(a) for a in d.get("articles", [])],
    )


def _part(d: dict) -> Part:
    return Part(
        type=d.get("type", "part"),
        number=d.get("number", ""),
        title=d.get("title", ""),
        chapters=[_chapter(c) for c in d.get("chapters", [])],
        articles=[_article(a) for a in d.get("articles", [])],
    )


def load_law(path: Path) -> Law:
    data = json.loads(path.read_text(encoding="utf-8"))
    return Law(
        type=data.get("type", "law"),
        name=data.get("name", ""),
        law_number=data.get("law_number"),
        source_file=data.get("source_file", path.name),
        parts=[_part(p) for p in data.get("parts", [])],
        chapters=[_chapter(c) for c in data.get("chapters", [])],
        articles=[_article(a) for a in data.get("articles", [])],
    )


# ============================================================
# 3. Chunker
# ============================================================
class LegalChunker:
    """Chia Law thành các Chunk.

    - chunk_level="article" (mặc định): 1 Điều = 1 chunk.
    - chunk_level="clause": 1 khoản = 1 chunk.
    - Tự tách theo khoản nếu Điều vượt max_chars (khi level="article").
    """

    def __init__(
        self,
        law: Law,
        chunk_level: str = "article",
        max_chars: int = 2500,
    ):
        self.law = law
        self.chunk_level = chunk_level
        self.max_chars = max_chars

    # ---------- duyệt cây ----------
    def chunks(self) -> Iterator[Chunk]:
        for part in self.law.parts:
            yield from self._walk_part(part)
        for chapter in self.law.chapters:
            yield from self._walk_chapter(chapter, part=None)
        for article in self.law.articles:
            yield from self._walk_article(article, None, None, None)

    def _walk_part(self, part: Part) -> Iterator[Chunk]:
        for chapter in part.chapters:
            yield from self._walk_chapter(chapter, part)
        for article in part.articles:
            yield from self._walk_article(article, part, None, None)

    def _walk_chapter(
        self, chapter: Chapter, part: Optional[Part]
    ) -> Iterator[Chunk]:
        for section in chapter.sections:
            for article in section.articles:
                yield from self._walk_article(
                    article, part, chapter, section
                )
        for article in chapter.articles:
            yield from self._walk_article(article, part, chapter, None)

    def _walk_article(
        self,
        article: Article,
        part: Optional[Part],
        chapter: Optional[Chapter],
        section: Optional[Section],
    ) -> Iterator[Chunk]:
        # Chế độ clause: mỗi khoản 1 chunk
        if self.chunk_level == "clause" and article.clauses:
            for clause in article.clauses:
                yield self._make_chunk(
                    article, clause, part, chapter, section
                )
            return

        # Chế độ article: nếu quá dài thì tự tách theo khoản
        full = self._render_article(article)
        if len(full) > self.max_chars and article.clauses:
            for clause in article.clauses:
                yield self._make_chunk(
                    article, clause, part, chapter, section
                )
            return

        yield self._make_chunk(article, None, part, chapter, section)

    # ---------- render nội dung ----------
    @staticmethod
    def _render_clause(c: Clause) -> str:
        lines = [f"{c.number}. {c.text}".rstrip()]
        for p in c.points:
            lines.append(f"  {p.number}) {p.text}".rstrip())
        return "\n".join(lines)

    def _render_article(
        self, a: Article, clause: Optional[Clause] = None
    ) -> str:
        if clause is not None:
            return self._render_clause(clause)
        lines = []
        if a.text:
            lines.append(a.text)
        for c in a.clauses:
            lines.append(self._render_clause(c))
        return "\n".join(lines).strip()

    # ---------- tạo chunk ----------
    def _make_chunk(
        self,
        a: Article,
        c: Optional[Clause],
        part: Optional[Part],
        chapter: Optional[Chapter],
        section: Optional[Section],
    ) -> Chunk:
        text = self._render_article(a, c)

        law_id = self.law.law_number or self.law.source_file.replace(".md", "")
        cid_parts = [law_id, f"dieu_{a.number}"]
        if c is not None:
            cid_parts.append(f"khoan_{c.number}")
        chunk_id = "__".join(cid_parts)

        # Breadcrumb
        bc: list[str] = []
        if self.law.name:
            head = self.law.name
            if self.law.law_number:
                head += f" ({self.law.law_number})"
            bc.append(head)
        if part:
            bc.append(f"Phần {part.number}. {part.title}".strip(". "))
        if chapter:
            bc.append(f"Chương {chapter.number}. {chapter.title}".strip(". "))
        if section:
            bc.append(f"Mục {section.number}. {section.title}".strip(". "))

        art_head = f"Điều {a.number}. {a.title}".strip(". ")
        if c is not None:
            art_head += f" — Khoản {c.number}"
        bc.append(art_head)

        breadcrumb = " > ".join(p for p in bc if p)
        ctx = f"{breadcrumb}\n\n{text}" if text else breadcrumb

        return Chunk(
            chunk_id=chunk_id,
            law_name=self.law.name.upper() if self.law.name else "",
            law_number=self.law.law_number or "",
            source_file=self.law.source_file,
            part_number=part.number if part else "",
            part_title=part.title if part else "",
            chapter_number=chapter.number if chapter else "",
            chapter_title=chapter.title if chapter else "",
            section_number=section.number if section else "",
            section_title=section.title if section else "",
            article_number=a.number,
            article_title=a.title,
            clause_number=c.number if c else "",
            chunk_level="clause" if c is not None else "article",
            text=text,
            contextualized_text=ctx,
            char_count=len(ctx),
            token_estimate=len(ctx) // 3,  # ước lượng thô cho tiếng Việt
        )


# ============================================================
# 4. IO
# ============================================================
def save_jsonl(chunks: list[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for ch in chunks:
            f.write(
                json.dumps(asdict(ch), ensure_ascii=False) + "\n"
            )


# ============================================================
# 5. main
# ============================================================
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "input", type=Path,
        help="File .json hoặc thư mục chứa các file .json đã parse",
    )
    ap.add_argument(
        "-o", "--output", type=Path, default=Path("chunks"),
    )
    ap.add_argument(
        "--level", choices=["article", "clause"],
        default="article",
        help="article: 1 Điều = 1 chunk; clause: 1 khoản = 1 chunk",
    )
    ap.add_argument(
        "--max-chars", type=int, default=2500,
        help="Ngưỡng tự tách clause khi chunk_level=article",
    )
    args = ap.parse_args()

    # Thu thập file .json
    if args.input.is_file():
        files = [args.input]
    elif args.input.is_dir():
        files = sorted(
            p for p in args.input.glob("*.json")
            if not p.name.endswith(".chunks.json")
            and not p.name.endswith(".chunks.jsonl")
        )
    else:
        raise SystemExit(f"Input không tồn tại: {args.input}")

    if not files:
        raise SystemExit(f"Không tìm thấy .json trong {args.input}")

    args.output.mkdir(parents=True, exist_ok=True)

    total = 0
    for src in files:
        law = load_law(src)
        chunker = LegalChunker(
            law,
            chunk_level=args.level,
            max_chars=args.max_chars,
        )
        chunks = list(chunker.chunks())
        dst = args.output / f"{src.stem}.chunks.jsonl"
        save_jsonl(chunks, dst)
        total += len(chunks)
        print(f"[OK] {src.name} -> {dst}  ({len(chunks)} chunks)")

    print(f"\nTổng: {len(files)} file, {total} chunks -> {args.output}/")


if __name__ == "__main__":
    main()