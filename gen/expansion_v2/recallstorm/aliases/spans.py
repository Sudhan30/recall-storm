"""Character span tracking and highlighting in ingredient strings."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Span:
    """Character offset interval [start, end) within a source string."""

    start: int
    end: int
    text: str
    label: str = ""


def span_from_match(text: str, start: int, end: int, label: str = "") -> Span:
    """Create a validated Span from a source string and [start, end) offsets."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if start < 0 or end < start or end > len(text):
        raise ValueError(f"Invalid span bounds [{start}, {end}) for text of length {len(text)}")
    return Span(start=start, end=end, text=text[start:end], label=label)


def span_text(text: str, span: Span) -> str:
    """Slice text using span.start and span.end."""
    return text[span.start : span.end]


def span_overlaps(s1: Span, s2: Span) -> bool:
    """Return True if two Spans overlap."""
    return max(s1.start, s2.start) < min(s1.end, s2.end)


def merge_spans(spans: list[Span]) -> list[Span]:
    """Merge overlapping Spans sorted by start offset."""
    if not spans:
        return []
    ordered = sorted(spans, key=lambda s: (s.start, s.end))
    merged: list[Span] = [ordered[0]]
    for cur in ordered[1:]:
        prev = merged[-1]
        if cur.start < prev.end:
            new_end = max(prev.end, cur.end)
            combined_text = prev.text + cur.text[max(0, prev.end - cur.start) :]
            merged[-1] = Span(prev.start, new_end, combined_text, prev.label or cur.label)
        else:
            merged.append(cur)
    return merged


def shift_span(span: Span, delta: int) -> Span:
    """Shift a Span's start and end offsets by delta."""
    if span.start + delta < 0:
        raise ValueError("Shifted span start cannot be negative")
    return Span(span.start + delta, span.end + delta, span.text, span.label)


def spans_to_offsets(spans: list[Span]) -> list[tuple[int, int]]:
    """Convert a list of Spans into (start, end) tuples."""
    return [(s.start, s.end) for s in spans]


def highlight_spans(text: str, spans: list[Span], marker: str = "**") -> str:
    """Wrap non-overlapping merged spans in text with marker."""
    merged = merge_spans(spans)
    if not merged:
        return text
    out: list[str] = []
    cursor = 0
    for sp in merged:
        out.append(text[cursor : sp.start])
        out.append(f"{marker}{text[sp.start : sp.end]}{marker}")
        cursor = sp.end
    out.append(text[cursor:])
    return "".join(out)


def span_to_dict(span: Span) -> dict:
    """Serialize a Span to a dictionary."""
    return {"start": span.start, "end": span.end, "text": span.text, "label": span.label}
