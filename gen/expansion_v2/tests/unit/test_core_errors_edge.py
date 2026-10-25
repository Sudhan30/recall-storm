"""Edge case tests for recallstorm.core.errors."""
import pytest
from recallstorm.core.errors import error_to_record, format_error


def test_standard_exception_handling():
    ve = ValueError("plain error")
    assert format_error(ve) == "[ValueError] plain error"
    rec = error_to_record(ve, src="custom/src.py")
    assert rec["code"] == "ValueError"
    assert rec["src"] == "custom/src.py"


def test_invalid_error_arg():
    with pytest.raises(TypeError):
        format_error("not an exception")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        error_to_record(None)  # type: ignore[arg-type]
