import pytest
from solution import paginate

ITEMS = [{"id": i, "value": f"v{i}"} for i in (10, 20, 30, 40, 50)]


def test_first_page_and_next_cursor():
    page, cursor = paginate(ITEMS, 2)
    assert [x["id"] for x in page] == [10, 20]
    assert cursor == 20


def test_followup_page_has_no_missing_record():
    page, cursor = paginate(ITEMS, 2, after=20)
    assert [x["id"] for x in page] == [30, 40]
    assert cursor == 40


def test_nonexistent_cursor_works():
    page, cursor = paginate(ITEMS, 2, after=25)
    assert [x["id"] for x in page] == [30, 40]
    assert cursor == 40


def test_last_page_has_no_next_cursor():
    page, cursor = paginate(ITEMS, 2, after=40)
    assert [x["id"] for x in page] == [50]
    assert cursor is None


def test_empty_result_and_no_input_mutation():
    original = [x.copy() for x in ITEMS]
    assert paginate(ITEMS, 2, after=99) == ([], None)
    assert ITEMS == original


def test_invalid_limit():
    with pytest.raises(ValueError):
        paginate(ITEMS, 0)
