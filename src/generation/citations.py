"""Tách, gỡ và gắn nhãn trích dẫn [chunk_id] trong câu trả lời (bước verify, spec mục 5)."""
import re

from src.ingestion.legal_chunker import article_key

CITE_RE = re.compile(r"[ \t]*\[([^\[\]]+)\]")
ID_RE = re.compile(r"[A-Z]+\d{4}_Dieu\w+")
NO_BASIS = "(chưa có căn cứ)"
_SEP_RE = re.compile(r"[,;\s]+")
_SPLIT_RE = re.compile(r"((?<=[.!?])\s+|\n+)")
_END_RE = re.compile(r"([.!?]*)$")


def _ids(inner):
    return [t for t in _SEP_RE.split(inner.strip()) if ID_RE.fullmatch(t)]


def cited_ids(text):
    """Mã trích dẫn trong `text` theo thứ tự xuất hiện, không trùng; ngoặc không chứa mã (vd [1]) bị bỏ qua."""
    return list(dict.fromkeys(cid for m in CITE_RE.finditer(text) for cid in _ids(m.group(1))))


def drop_citations(text, bad):
    """Gỡ các mã thuộc tập `bad` khỏi `text`; ngoặc không còn mã nào thì gỡ cả ngoặc. Trả str."""
    def fix(m):
        ids = _ids(m.group(1))
        keep = [cid for cid in ids if cid not in bad]
        if keep == ids:
            return m.group(0)  # không có gì để gỡ (kể cả ngoặc thường như [1])
        return f" [{', '.join(keep)}]" if keep else ""
    return CITE_RE.sub(fix, text)


def normalize_ids(text, known):
    """Đổi mã cấp Khoản về mã cấp Điều khi ngữ cảnh chỉ có đoạn cấp Điều (câu direct dùng get_article).

    Args:
        text: câu trả lời.
        known: tập hoặc dict có chunk_id làm khóa.
    """
    def fix(m):
        ids = [cid if cid in known or article_key(cid) not in known else article_key(cid) for cid in _ids(m.group(1))]
        return m.group(0) if ids == _ids(m.group(1)) else f" [{', '.join(dict.fromkeys(ids))}]"
    return CITE_RE.sub(fix, text)


def strip_unknown(text, known):
    """verify(a): gỡ mã không có trong ngữ cảnh.

    Args:
        text: câu trả lời.
        known: tập hoặc dict có chunk_id làm khóa (các đoạn đã đưa vào ngữ cảnh).

    Returns:
        (văn bản đã gỡ, danh sách mã đã gỡ).
    """
    removed = [cid for cid in cited_ids(text) if cid not in known]
    return drop_citations(text, set(removed)), removed


def sentences(text):
    """Tách câu giữ nguyên khoảng trắng: phần tử chẵn là câu, phần tử lẻ là phần phân cách; ''.join(...) == text."""
    return _SPLIT_RE.split(text)


def cited_sentences(text):
    """Danh sách (chỉ số trong sentences(text), câu, các mã) cho những câu có trích dẫn."""
    parts = sentences(text)
    return [(i, parts[i], cited_ids(parts[i])) for i in range(0, len(parts), 2) if cited_ids(parts[i])]


def drop_pairs(text, verdicts):
    """Gỡ các cặp mà bước kiểm chứng LLM cho là không được hỗ trợ.

    Args:
        text: câu trả lời.
        verdicts: {chỉ số câu trong sentences(text): tập mã cần gỡ khỏi câu đó}.
    """
    return "".join(drop_citations(p, verdicts[i]) if i in verdicts else p for i, p in enumerate(sentences(text)))


def lost_sentences(before, after):
    """Chỉ số các câu có trích dẫn trong `before` nhưng không còn mã nào trong `after`."""
    old, new = sentences(before), sentences(after)
    return [i for i in range(0, min(len(old), len(new)), 2) if cited_ids(old[i]) and not cited_ids(new[i])]


def label_sentences(text, indices):
    """Gắn NO_BASIS vào cuối các câu có chỉ số trong `indices`, đặt trước dấu kết câu."""
    marked = set(indices)
    return "".join(_END_RE.sub(lambda m: f" {NO_BASIS}{m.group(1)}", p.rstrip(), count=1) if i in marked else p
                   for i, p in enumerate(sentences(text)))
