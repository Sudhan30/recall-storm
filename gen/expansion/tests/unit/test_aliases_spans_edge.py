"""Edge tests for recallstorm.aliases.spans."""
import pytest
from recallstorm.aliases.spans import (
    Span,
    merge_spans,
    span_from_match,
    span_text,
)


def test_spans_edge():
    assert merge_spans([]) == []
    with pytest.raises(ValueError):
        Span(-1, 5)
    with pytest.raises(ValueError):
        Span(6, 5)
    with pytest.raises(ValueError):
        span_from_match(None)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        span_text("abc", Span(0, 10))
