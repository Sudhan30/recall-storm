"""Edge case tests for recallstorm.aliases.spans."""
import pytest
from recallstorm.aliases.spans import highlight_spans, merge_spans, shift_span, span_from_match


def test_spans_edge():
    with pytest.raises(ValueError):
        span_from_match("ABC", -1, 2)
    with pytest.raises(ValueError):
        span_from_match("ABC", 2, 1)
    with pytest.raises(ValueError):
        span_from_match("ABC", 0, 10)
    sp = span_from_match("ABC", 1, 2)
    with pytest.raises(ValueError):
        shift_span(sp, -5)
    assert merge_spans([]) == []
    assert highlight_spans("ABC", []) == "ABC"
