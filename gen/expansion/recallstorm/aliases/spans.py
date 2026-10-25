"""Character offset Span utilities for ingredient evidence extraction."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Span:
    """Character offset interval [start, end) with label."""

    start: int
    end: int
    label: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.start, int) or not isinstance(self.end, int):
            raise TypeError("Span start and end must be integers")
        if self.start < 0 or self.end < self.start:
            raise ValueError(f"Invalid span bounds: [{self.start}, {self.end})")


def span_from_match(m: re.Match, label: str = "") -> Span:
    """Construct a Span from a regex Match object."""
    if m is None:
        raise ValueError("Match object cannot be None")
    return Span(start=m.start(), end=m.end(), label=label)


def span_text(text: str, span: Span) -> str:
    """Slice text using a Span's [start, end) offsets."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if span.end > len(text):
        raise ValueError("Span end exceeds text length")
    return text[span.start:span.end]


def span_overlaps(s1: Span, s2: Span) -> bool:
    """Return True if two spans overlap."""
    return max(s1.start, s2.start) < min(s1.end, s2.end)


def merge_spans(spans: list[Span]) -> list[Span]:
    """Sort and merge overlapping spans."""
    if not spans:
        return []
    ordered = sorted(spans, key=lambda s: (s.start, s.end))
    merged: list[Span] = [ordered[0]]
    for cur in ordered[1:]:
        prev = merged[-1]
        if cur.start < prev.end:
            merged[-1] = Span(start=prev.start, end=max(prev.end, cur.end), label=prev.label or cur.label)
        else:
            merged.append(cur)
    return merged


def shift_span(span: Span, offset: int) -> Span:
    """Shift a Span by a signed integer character offset."""
    return Span(start=span.start + offset, end=span.end + offset, label=span.label)


def spans_to_offsets(spans: list[Span]) -> list[tuple[int, int]]:
    """Convert a list of Spans to (start, end) tuples."""
    return [(s.start, s.end) for s in spans]


def highlight_spans(text: str, spans: list[Span], marker: str = "**") -> str:
    """Insert highlight markers around non-overlapping merged spans in text."""
    if not spans:
        return text
    merged = merge_spans(spans)
    parts: list[str] = []
    cursor = 0
    for s in merged:
        parts.append(text[cursor:s.start])
        parts.append(f"{marker}{text[s.start:s.end]}{marker}")
        cursor = s.end
    parts.append(text[cursor:])
    return "".join(parts)


def span_to_dict(span: Span) -> dict:
    """Convert a Span to a dictionary."""
    return {"start": span.start, "end": span.end, "label": span.label}
