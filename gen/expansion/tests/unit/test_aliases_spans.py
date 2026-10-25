"""Unit tests for recallstorm.aliases.spans."""
import re
from recallstorm.aliases.spans import (
    Span,
    highlight_spans,
    merge_spans,
    shift_span,
    span_from_match,
    span_overlaps,
    span_text,
    span_to_dict,
    spans_to_offsets,
)


def test_spans_operations():
    text = "SUGAR, FD&C RED #3, WATER"
    m = re.search(r"FD&C RED #3", text)
    assert m is not None
    sp = span_from_match(m, "RED3")
    assert span_text(text, sp) == "FD&C RED #3"
    assert span_overlaps(sp, Span(10, 15)) is True
    merged = merge_spans([sp, Span(10, 15, "RED3")])
    assert len(merged) == 1
    shifted = shift_span(sp, 2)
    assert shifted.start == sp.start + 2
    assert spans_to_offsets([sp]) == [(7, 18)]
    assert highlight_spans(text, [sp], "[") == "SUGAR, [FD&C RED #3[, WATER"
    assert span_to_dict(sp)["label"] == "RED3"
