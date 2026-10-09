import pytest

from src.ingestion.legal_chunker import chunk_law, fixed_chunk

META = {
    "law_id": "BLDS2015",
    "document": "Bộ luật Dân sự 2015",
    "effective_date": "2017-01-01",
    "status": "Còn hiệu lực",
}

SAMPLE = """# BỘ LUẬT DÂN SỰ

## Chương XVIII
NGHĨA VỤ

### Mục 2. Thực hiện nghĩa vụ

**Điều 357. Trách nhiệm do chậm thực hiện nghĩa vụ trả tiền**

1. Trường hợp bên có nghĩa vụ chậm trả tiền thì bên đó phải trả lãi.

2. Lãi suất được xác định như sau:
a) Theo thỏa thuận của các bên;
b) Theo quy định của luật.

Điều 358. Điều không có khoản
Nội dung của điều này nằm ngay dưới tiêu đề.

Điều 359a. Điều có số kèm chữ
Nội dung điều 359a.
"""


@pytest.fixture
def chunks():
    return chunk_law(SAMPLE, META)


def test_one_chunk_per_clause_and_per_clauseless_article(chunks):
    assert [c["chunk_id"] for c in chunks] == [
        "BLDS2015_Dieu357_Khoan1",
        "BLDS2015_Dieu357_Khoan2",
        "BLDS2015_Dieu358",
        "BLDS2015_Dieu359a",
    ]


def test_hierarchy_metadata(chunks):
    c = chunks[0]
    assert c["chapter"] == "Chương XVIII"
    assert c["section"] == "Mục 2"
    assert c["article"] == "Điều 357"
    assert c["article_title"] == "Trách nhiệm do chậm thực hiện nghĩa vụ trả tiền"
    assert c["clause"] == "Khoản 1"
    assert c["document"] == "Bộ luật Dân sự 2015"
    assert c["effective_date"] == "2017-01-01"
    assert c["status"] == "Còn hiệu lực"


def test_points_stay_inside_their_clause(chunks):
    content = chunks[1]["content"]
    assert content.startswith("Lãi suất được xác định như sau:")
    assert "a) Theo thỏa thuận của các bên;" in content
    assert "b) Theo quy định của luật." in content


def test_clauseless_article_has_no_clause(chunks):
    assert chunks[2]["clause"] is None
    assert chunks[2]["content"] == "Nội dung của điều này nằm ngay dưới tiêu đề."


def test_markdown_noise_is_stripped(chunks):
    assert all("**" not in c["article_title"] and "#" not in c["content"] for c in chunks)


def test_duplicate_chunk_id_raises():
    with pytest.raises(ValueError, match="BLDS2015_Dieu1"):
        chunk_law("Điều 1. A\nx\nĐiều 1. B\ny\n", META)


def test_text_without_articles_raises():
    with pytest.raises(ValueError):
        chunk_law("không có điều nào cả", META)


def test_fixed_chunk_overlaps_and_covers_text():
    text = " ".join(f"w{i}" for i in range(25))
    out = fixed_chunk(text, META, size=10, overlap=2)
    assert [c["chunk_id"] for c in out] == ["BLDS2015_fixed0", "BLDS2015_fixed1", "BLDS2015_fixed2"]
    assert out[0]["content"].split()[-2:] == out[1]["content"].split()[:2]
    assert out[-1]["content"].split()[-1] == "w24"


def test_expiry_date_copied_from_meta():
    meta = {**META, "law_id": "BLLD2012", "expiry_date": "2021-01-01", "status": "Hết hiệu lực"}
    assert {c["expiry_date"] for c in chunk_law(SAMPLE, meta)} == {"2021-01-01"}


def test_missing_expiry_date_means_still_effective(chunks):
    # META không có khóa expiry_date (laws.json cũ) -> coi là còn hiệu lực
    assert all(c["expiry_date"] is None for c in chunks)


def test_fixed_chunk_records_articles_spanned():
    # mỗi Điều 11 từ: 3 từ tiêu đề + 8 từ nội dung
    text = "Điều 1. A\n" + " ".join(["x"] * 8) + "\nĐiều 2. B\n" + " ".join(["y"] * 8)
    out = fixed_chunk(text, META, size=10, overlap=0)
    assert [c["articles"] for c in out] == [["Điều 1"], ["Điều 1", "Điều 2"], ["Điều 2"]]


def test_fixed_chunk_window_starting_mid_article_keeps_that_article():
    text = "Điều 7. A\n" + " ".join(["x"] * 30)
    out = fixed_chunk(text, META, size=10, overlap=0)
    assert out[2]["articles"] == ["Điều 7"]


def test_fixed_chunk_ignores_inline_article_reference():
    text = "Điều 1. A\nTheo quy định tại Điều 5. thì bên vi phạm phải bồi thường."
    assert fixed_chunk(text, META, size=50, overlap=0)[0]["articles"] == ["Điều 1"]


def test_fixed_chunk_text_outside_articles_has_no_article():
    text = "BỘ LUẬT DÂN SỰ\nChương I\nQUY ĐỊNH CHUNG"
    assert fixed_chunk(text, META, size=50, overlap=0)[0]["articles"] == []


@pytest.mark.parametrize("size, overlap", [(10, 10), (10, 12), (10, -1)])
def test_fixed_chunk_rejects_invalid_overlap(size, overlap):
    with pytest.raises(ValueError):
        fixed_chunk("a b c", META, size=size, overlap=overlap)
