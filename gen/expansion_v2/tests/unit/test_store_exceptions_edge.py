"""Edge case tests for recallstorm.store.exceptions."""
from contract import ExceptionKind, StoreNote
from recallstorm.store.exceptions import exception_kind_for_text, exceptions_for_store


def test_store_exceptions_edge():
    assert exception_kind_for_text("") == ExceptionKind.NOT_ON_PLANOGRAM
    assert exceptions_for_store([StoreNote("N1", "WM1", "text")], "WM999") == []
