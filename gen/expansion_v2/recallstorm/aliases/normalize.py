"""Ingredient string normalization, OCR error fixing, and offset mapping."""
from __future__ import annotations

import re
import unicodedata


def fold_unicode(text: str) -> str:
    """Fold Unicode characters to ASCII equivalents preserving character positions where possible."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def ocr_fix(text: str) -> str:
    """Fix common 1-to-1 OCR character confusions in color/additive mentions while preserving length."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    # Preserve exact string length so character offsets remain identical
    out = re.sub(r"(?i)\bREO(\s+(?:NO\.?\s*|#)?3)\b", r"RED\1", text)
    out = re.sub(r"(?i)\bRED\s+N0(\.?\s*3)\b", r"RED NO\1", out)
    out = re.sub(r"(?i)\bE1Z7\b", "E127", out)
    out = re.sub(r"(?i)\bEI27\b", "E127", out)
    out = re.sub(r"(?i)\bERYTHR0SINE\b", "ERYTHROSINE", out)
    return out


def strip_punctuation(text: str) -> str:
    """Replace punctuation characters (except & and #) with spaces, preserving length."""
    return re.sub(r"[^\w\s&#]", " ", text)


def collapse_whitespace(text: str) -> str:
    """Collapse consecutive whitespace into single spaces and strip ends."""
    return " ".join(text.split())


def normalize_ingredients(text: str) -> str:
    """Normalize an ingredient string into uppercase with collapsed whitespace."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    fixed = ocr_fix(fold_unicode(text))
    return collapse_whitespace(fixed).upper()


def tokenize_ingredients(text: str) -> list[str]:
    """Split an ingredient statement into top-level comma/semicolon-separated tokens."""
    if not isinstance(text, str) or not text.strip():
        return []
    parts = re.split(r"[,;]+", text)
    return [p.strip().strip(".") for p in parts if p.strip().strip(".")]


def split_sub_ingredients(text: str) -> list[str]:
    """Split an ingredient string on commas, parentheses, and brackets into leaf ingredients."""
    if not isinstance(text, str) or not text.strip():
        return []
    parts = re.split(r"[,;()\[\]{}|:]+", text)
    return [p.strip().strip(".") for p in parts if p.strip().strip(".")]


def ingredient_offsets(text: str) -> list[tuple[str, int, int]]:
    """Return (token, start, end) for every leaf ingredient segment in text."""
    if not isinstance(text, str):
        return []
    out: list[tuple[str, int, int]] = []
    for m in re.finditer(r"[^,;()\[\]{}|:.]+", text):
        raw = m.group(0)
        lstrip_len = len(raw) - len(raw.lstrip())
        rstrip_len = len(raw) - len(raw.rstrip())
        s = m.start() + lstrip_len
        e = m.end() - rstrip_len
        if e > s:
            out.append((text[s:e], s, e))
    return out


def denormalize_span(orig_text: str, norm_span: tuple[int, int]) -> tuple[int, int]:
    """Clamp or map a span back onto orig_text bounds."""
    s = max(0, min(len(orig_text), norm_span[0]))
    e = max(s, min(len(orig_text), norm_span[1]))
    return (s, e)
