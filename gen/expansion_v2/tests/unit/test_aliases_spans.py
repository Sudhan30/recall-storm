"""Unit tests for recallstorm.aliases.spans."""
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
    txt = "SUGAR, FD&C RED #3, SALT"
    sp = span_from_match(txt, 7, 18, "RED3")
    assert isinstance(sp, Span)
    assert span_text(txt, sp) == "FD&C RED #3"
    sp2 = span_from_match(txt, 12, 18, "RED3")
    assert span_overlaps(sp, sp2)
    merged = merge_spans([sp2, sp])
    assert len(merged) == 1 and merged[0].start == 7 and merged[0].end == 18
    shifted = shift_span(sp, 3)
    assert shifted.start == 10 and shifted.end == 21
    assert spans_to_offsets([sp]) == [(7, 18)]
    assert highlight_spans(txt, [sp]) == "SUGAR, **FD&C RED #3**, SALT"
    assert span_to_dict(sp)["label"] == "RED3"
