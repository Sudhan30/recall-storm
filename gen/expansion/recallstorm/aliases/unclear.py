"""Detect vague generic color declarations and unreadable/corrupted ingredient labels."""
from __future__ import annotations

import re

_GENERIC_COLOR_RE = re.compile(
    r"\b(?:"
    r"artificial\s+colors?(?!\s*(?:[\(\[\:]|\s+fd&c|\s+red|\s+yellow|\s+blue|\s+green))"
    r"|color\s+added"
    r"|artificial\s+coloring"
    r"|fd&c\s+colors?(?!\s*(?:[\(\[\:]|\s+red|\s+yellow|\s+blue))"
    r"|certified\s+colors?"
    r"|u\.?s\.?\s+certified\s+colors?"
    r")\b",
    re.IGNORECASE,
)


def generic_color_phrases(text: str) -> list[str]:
    """Return any vague generic color phrases that do not specify which dye is used."""
    if not isinstance(text, str) or not text.strip():
        return []
    hits: list[str] = []
    for m in _GENERIC_COLOR_RE.finditer(text):
        after = text[m.end():m.end() + 25]
        if re.match(r"^\s*[\(\[\:]\s*(?:fd&c|red|yellow|blue|annatto|carmine|caramel|beta|turmeric)", after, re.IGNORECASE):
            continue
        if re.search(r"\b(?:RED\s*(?:NO\.?\s*|#)?\s*(?:3|40)|YELLOW\s*(?:NO\.?\s*|#)?\s*[56]|BLUE\s*(?:NO\.?\s*|#)?\s*[12]|E127)\b", text, re.IGNORECASE):
            continue
        hits.append(m.group(0))
    return hits


def is_generic_color(text: str) -> bool:
    """Return True if the label declares generic artificial color without listing specific dyes."""
    return len(generic_color_phrases(text)) > 0


def ocr_noise_ratio(text: str) -> float:
    """Calculate the fraction of non-standard/garbled characters in text."""
    if not isinstance(text, str) or not text:
        return 1.0
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ,.;:()[]&-#'%/|\n\t")
    noisy = sum(1 for ch in text if ch not in allowed and ord(ch) < 128 or ch in "?~^_\\@$*")
    return noisy / max(1, len(text))


def truncated_label(text: str) -> bool:
    """Return True if the ingredient statement appears truncated mid-token or mid-parenthesis."""
    if not isinstance(text, str) or not text.strip():
        return True
    s = text.strip()
    if s.endswith(("...", "…", "[TRUNCATED]", "UNREADABLE", "ILLEGIBLE")):
        return True
    if s.count("(") > s.count(")") + 1:
        return True
    return False


def is_unreadable(text: str) -> bool:
    """Return True if the ingredient text is empty, heavily garbled, or explicitly unreadable."""
    if not isinstance(text, str) or len(text.strip()) < 3:
        return True
    low = text.lower()
    if any(tok in low for tok in ("unreadable", "illegible", "smudged", "missing label", "???")):
        return True
    if ocr_noise_ratio(text) > 0.12:
        return True
    return False


def readability_score(text: str) -> float:
    """Return a readability score in [0.0, 1.0]."""
    if not isinstance(text, str) or not text.strip():
        return 0.0
    if is_unreadable(text):
        return max(0.0, 0.4 - ocr_noise_ratio(text))
    return round(max(0.0, 1.0 - ocr_noise_ratio(text)), 3)


def unclear_reason(text: str) -> str | None:
    """Return a human-readable explanation if the label requires HOLD_VERIFY, else None."""
    if is_unreadable(text):
        return "Ingredient label is unreadable, missing, or corrupted"
    if truncated_label(text):
        return "Ingredient label is truncated"
    phrases = generic_color_phrases(text)
    if phrases:
        return f"Vague color declaration ('{phrases[0]}') without specific dye breakdown"
    return None


def needs_human_review(text: str) -> bool:
    """Return True if the label is unclear and requires human review (HOLD_VERIFY)."""
    return unclear_reason(text) is not None


def redact_noise(text: str) -> str:
    """Strip OCR noise characters from text."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return re.sub(r"[?~^_\\@$*]+", " ", text).strip()
