"""Ingredient normalization, OCR repair, tokenization, and offset preservation."""
from __future__ import annotations

import re
from recallstorm.aliases.translations import accent_fold


def fold_unicode(text: str) -> str:
    """Fold Unicode accents while preserving string length."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return accent_fold(text)


def ocr_fix(text: str) -> str:
    """Repair common OCR digit/letter substitutions in dye and E-number tokens."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    out = re.sub(r"\bEl27\b", "E127", text)
    out = re.sub(r"\bE1Z7\b", "E127", out)
    out = re.sub(r"\bFD&C\s+RED\s+#?O3\b", "FD&C RED #3", out, flags=re.IGNORECASE)
    return out


def strip_punctuation(text: str) -> str:
    """Replace punctuation characters (except # and &) with spaces, preserving length."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return "".join(ch if (ch.isalnum() or ch in "#& ") else " " for ch in text)


def collapse_whitespace(text: str) -> str:
    """Collapse consecutive whitespace characters into a single space."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return " ".join(text.split())


def normalize_ingredients(text: str) -> str:
    """Normalize an ingredient statement to uppercase collapsed ASCII."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return collapse_whitespace(fold_unicode(ocr_fix(text))).upper()


def tokenize_ingredients(text: str) -> list[str]:
    """Split an ingredient string on commas, semicolons, and pipes into top-level tokens."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    tokens = re.split(r"[,;|]+", text)
    return [t.strip() for t in tokens if t.strip()]


def split_sub_ingredients(text: str) -> list[str]:
    """Split an ingredient statement on commas as well as parentheses/brackets."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    parts = re.split(r"[,;|()\[\]{}:]+", text)
    return [p.strip().rstrip(".") for p in parts if p.strip().rstrip(".")]


def ingredient_offsets(text: str) -> list[tuple[str, int, int]]:
    """Return (sub_ingredient, start, end) offsets for each leaf ingredient phrase."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    out: list[tuple[str, int, int]] = []
    for m in re.finditer(r"[^,;|()\[\]{}:]+", text):
        raw = m.group(0)
        lstripped = raw.lstrip()
        rstripped = lstripped.rstrip(" .")
        if not rstripped:
            continue
        start = m.start() + (len(raw) - len(lstripped))
        end = start + len(rstripped)
        out.append((rstripped, start, end))
    return out


def denormalize_span(orig_text: str, norm_start: int, norm_end: int) -> tuple[int, int]:
    """Clamp or map normalized offsets back to valid indices on orig_text."""
    if not isinstance(orig_text, str):
        raise TypeError("orig_text must be a string")
    if norm_start < 0 or norm_end < norm_start:
        raise ValueError("Invalid span offsets")
    n = len(orig_text)
    return min(norm_start, n), min(norm_end, n)
