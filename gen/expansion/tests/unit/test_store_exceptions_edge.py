"""Edge tests for recallstorm.store.exceptions."""
import pytest
from recallstorm.store.exceptions import (
    exception_kind_for_text,
    parse_note,
)


def test_exceptions_edge():
    with pytest.raises(ValueError):
        exception_kind_for_text("")
    with pytest.raises(TypeError):
        parse_note("not_a_note")  # type: ignore[arg-type]
