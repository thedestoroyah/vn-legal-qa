import pytest

from src.retrieval.filters import check_date, chroma_where, is_valid_at

OLD = {"effective_date": "2013-05-01", "expiry_date": "2021-01-01"}
NEW = {"effective_date": "2021-01-01", "expiry_date": None}


@pytest.mark.parametrize("date, old, new", [(None, False, True), ("2020-12-31", True, False),
                                            ("2021-01-01", False, True), ("2013-05-01", True, False),
                                            ("2010-01-01", False, False)])
def test_is_valid_at_boundaries(date, old, new):
    assert (is_valid_at(OLD, date), is_valid_at(NEW, date)) == (old, new)


@pytest.mark.parametrize("bad", ["2020", "01/03/2020", "2020-13-01", "hôm qua"])
def test_bad_date_rejected(bad):
    with pytest.raises(ValueError):
        is_valid_at(NEW, bad)
    with pytest.raises(ValueError):
        chroma_where(bad)


def test_compact_date_is_normalized():
    assert check_date("20200301") == "2020-03-01"
    assert check_date(None) is None


def test_chroma_where_shapes():
    assert chroma_where() == {"effective_to": {"$eq": 99991231}}
    assert chroma_where("2020-03-01") == {"$and": [{"effective_from": {"$lte": 20200301}},
                                                   {"effective_to": {"$gt": 20200301}}]}


from src.retrieval.filters import ANY_DATE


def test_any_date_accepts_every_version():
    expired = {"effective_date": "2013-05-01", "expiry_date": "2021-01-01"}
    future = {"effective_date": "2099-01-01", "expiry_date": None}
    assert check_date(ANY_DATE) == ANY_DATE
    assert is_valid_at(expired, ANY_DATE) and is_valid_at(future, ANY_DATE)


def test_chroma_where_any_is_none():
    assert chroma_where(ANY_DATE) is None
