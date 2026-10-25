"""Edge tests for recallstorm.core.errors."""
import pytest
from recallstorm.core.errors import (
    RecallStormError,
    error_to_record,
    format_error,
)


def test_empty_message_fallback():
    e = RecallStormError("")
    assert e.message == "Unspecified RecallStormError"


def test_standard_exception_handling():
    ve = ValueError("plain error")
    assert format_error(ve) == "[ValueError] plain error"
    rec = error_to_record(ve)
    assert rec["code"] == "ValueError"
    assert rec["details"] == {}


def test_invalid_inputs():
    with pytest.raises(TypeError):
        format_error("not_an_exception")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        error_to_record("not_an_exception")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        error_to_record(ValueError("x"), "")
