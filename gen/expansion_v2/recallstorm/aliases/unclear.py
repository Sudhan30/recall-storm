"""Detect ambiguous color statements and unreadable/truncated OCR labels."""
from __future__ import annotations

import re

_GENERIC_COLOR_RE = re.compile(
    r"\b(?:ARTIFICIAL\s+COLORS?|COLORS?\s+ADDED|ARTIFICIAL\s+COLORING|CERTIFIED\s+COLORS?|FD&C\s+COLORS?|U\.?S\.?\s+CERTIFIED\s+COLORS?)\b",
    re.IGNORECASE,
)
_SPECIFIC_COLOR_RE = re.compile(
    r"\b(?:RED\s*(?:NO\.?\s*|#)?(?:3|40)|YELLOW\s*(?:NO\.?\s*|#)?(?:5|6)|BLUE\s*(?:NO\.?\s*|#)?(?:1|2)|GREEN\s*(?:NO\.?\s*|#)?3|CARMINE|ANNATTO|TURMERIC|BETA\s*CAROTENE|TITANIUM\s+DIOXIDE|CARAMEL\s+COLOR|BEET\s+JUICE|PAPRIKA|E127)\b",
    re.IGNORECASE,
)


def generic_color_phrases(text: str) -> list[tuple[str, int, int]]:
    """Return all generic color phrases (matched_text, start, end) in text."""
    if not isinstance(text, str):
        return []
    return [(m.group(0), m.start(), m.end()) for m in _GENERIC_COLOR_RE.finditer(text)]


def is_generic_color(text: str) -> bool:
    """Return True if text mentions generic artificial color WITHOUT specifying which FD&C/natural colors."""
    if not isinstance(text, str) or not text.strip():
        return False
    has_generic = bool(_GENERIC_COLOR_RE.search(text))
    if not has_generic:
        return False
    # If the label explicitly lists the specific colors (e.g., 'ARTIFICIAL COLORS (RED 40, YELLOW 5)'), it is NOT ambiguous
    has_specific = bool(_SPECIFIC_COLOR_RE.search(text))
    return not has_specific


def ocr_noise_ratio(text: str) -> float:
    """Return fraction of characters in text that are OCR noise/garbled symbols."""
    if not isinstance(text, str) or not text:
        return 1.0
    weird = sum(1 for c in text if c in "?~^`\\|@#$%*_<>")
    return weird / len(text)


def truncated_label(text: str) -> bool:
    """Return True if an ingredient label is visibly truncated or cut off mid-word."""
    if not isinstance(text, str):
        return True
    s = text.strip()
    if not s:
        return True
    if s.endswith("...") or s.endswith("..") or s.endswith("[TRUNCATED]"):
        return True
    if re.search(r"\b(?:FD&C|ARTIFICIAL|COLOR|RED)\s*$", s, re.IGNORECASE):
        return True
    return False


def is_unreadable(text: str) -> bool:
    """Return True if the ingredient string is empty, garbled, or truncated."""
    if not isinstance(text, str) or len(text.strip()) < 3:
        return True
    if any(tok in text.upper() for tok in ("UNREADABLE", "ILLEGIBLE", "SMUDGED", "???")):
        return True
    if ocr_noise_ratio(text) > 0.12:
        return True
    return truncated_label(text)


def readability_score(text: str) -> float:
    """Return a readability score in [0.0, 1.0]."""
    if not isinstance(text, str) or not text.strip():
        return 0.0
    score = 1.0 - min(1.0, ocr_noise_ratio(text) * 4.0)
    if truncated_label(text):
        score *= 0.4
    return round(max(0.0, min(1.0, score)), 3)


def unclear_reason(text: str) -> str | None:
    """Return a human-readable reason why the label requires HOLD_VERIFY, or None if clear."""
    if is_unreadable(text):
        return "Label is unreadable, smudged, or truncated"
    if is_generic_color(text):
        return "Label declares unspecified artificial/certified color without naming specific dyes"
    return None


def needs_human_review(text: str) -> bool:
    """Return True if the label is unclear and requires HOLD_VERIFY."""
    return unclear_reason(text) is not None


def redact_noise(text: str) -> str:
    """Replace OCR noise characters with spaces."""
    if not isinstance(text, str):
        return ""
    return re.sub(r"[?~^`\\|@#$%*_<>]+", " ", text)
