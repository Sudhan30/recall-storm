"""Normalize ingredient text and detect additive aliases with span accuracy."""
from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class AliasMatch:
    additive: str
    canonical_alias: str
    match_text: str
    start: int
    end: int


_LEET_MAP = str.maketrans({
    "0": "o",
    "1": "i",
    "3": "e",
    "5": "s",
})


def normalize_text(text: str) -> str:
    """Return lowercase whitespace-normalized text with common OCR fixes applied."""
    lowered = text.lower()
    cleaned = re.sub(r"[\s\-_/]+", " ", lowered)
    return cleaned.strip()


# Explicit decoy patterns that must never be matched as Red No. 3
_DECOY_PATTERNS: tuple[re.Pattern[str], ...] = (
    # D&C Red No. 3 / 33 / 30 etc. (cosmetic/drug D&C dyes, not FD&C Red 3)
    re.compile(r"\b(?<!f)d\s*&\s*c\s+red(?:\s+(?:dye|no\.?|number|#))?\s*\d+\b", re.IGNORECASE),
    # Red 40, Red 33, Red 30, Red 2, Red 28, etc. (any number other than 3 or 03)
    re.compile(
        r"\b(?:fd\s*&\s*c\s+)?red(?:\s+(?:dye|no\.?|number|lake|#))*\s*#?\s*(?:[124-9]\d*|3\d+|0*[124-9]\d*)\b",
        re.IGNORECASE,
    ),
    # Quantified nouns like "3 red apples", "3 red peppers", "red 3-bean"
    re.compile(r"\b3\s+red\s+[a-z]+\b", re.IGNORECASE),
    re.compile(r"\bred\s+3\s*-\s*[a-z]+\b", re.IGNORECASE),
)


# Patterns for RED3 aliases capturing exact character spans in original text
_RED3_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "FD&C Red No. 3",
        re.compile(
            r"\bfd\s*(?:&|and)\s*c\s+red(?:\s+(?:dye|no\.?|number|num\.?))?\s*#?\s*0*3(?:\s+lake)?\b(?!\d)",
            re.IGNORECASE,
        ),
    ),
    (
        "Red No. 3",
        re.compile(
            r"(?<![a-z0-9&])\bred\s+(?:no\.?|number|num\.?)\s*#?\s*0*3(?:\s+lake)?\b(?!\d)",
            re.IGNORECASE,
        ),
    ),
    (
        "Red Dye 3",
        re.compile(
            r"(?<![a-z0-9&])\bred\s+dye\s*(?:no\.?|number|#)?\s*0*3(?:\s+lake)?\b(?!\d)",
            re.IGNORECASE,
        ),
    ),
    (
        "Red 3",
        re.compile(
            r"(?<![a-z0-9&])\bred\s*(?:#\s*)?0*3(?:\s+(?:dye|lake))?\b(?!\s*[-a-z]*\b(?:bean|pepper|apple|chili|berry|cherries|potato|onion|lentil)|\d)",
            re.IGNORECASE,
        ),
    ),
    (
        "erythrosine",
        re.compile(
            r"\be[\W_]*r[\W_]*[y1i][\W_]*t[\W_]*h[\W_]*r[\W_]*[o0][\W_]*[s5][\W_]*[i1l][\W_]*n[\W_]*e?(?:\s+b)?\b",
            re.IGNORECASE,
        ),
    ),
    (
        "E127",
        re.compile(
            r"\be\s*[-–]?\s*127\b(?!\d)",
            re.IGNORECASE,
        ),
    ),
    (
        "CI 45430",
        re.compile(
            r"\bc\.?i\.?\s*45430\b(?!\d)",
            re.IGNORECASE,
        ),
    ),
)

_UNCLEAR_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bartificial\s+colou?rs?\b", re.IGNORECASE),
    re.compile(r"\bartificial\s+colou?ring\b", re.IGNORECASE),
    re.compile(r"\bcolou?r\s+added\b", re.IGNORECASE),
    re.compile(r"\badded\s+colou?r\b", re.IGNORECASE),
    re.compile(r"\bfd\s*&\s*c\s+colou?rs?\b", re.IGNORECASE),
    re.compile(r"\bcitric\s+acid\s+and\s+colou?r\b", re.IGNORECASE),
    re.compile(r"\bunreadable\b", re.IGNORECASE),
    re.compile(r"\billegible\b", re.IGNORECASE),
    re.compile(r"\bsmudged\b", re.IGNORECASE),
    re.compile(r"\?\?\?+", re.IGNORECASE),
)


def _overlaps_decoy(text: str, start: int, end: int) -> bool:
    for pat in _DECOY_PATTERNS:
        for m in pat.finditer(text):
            if max(start, m.start()) < min(end, m.end()):
                return True
    # Also check immediately preceding "D&C " (without F)
    prefix = text[max(0, start - 10):start]
    if re.search(r"(?<![fF])d\s*&\s*c\s*$", prefix, re.IGNORECASE):
        return True
    return False


def _build_dynamic_alias_pattern(alias: str) -> re.Pattern[str]:
    tokens = [re.escape(tok) for tok in re.split(r"\s+", alias.strip()) if tok]
    body = r"\s+".join(tokens)
    return re.compile(rf"(?<![a-z0-9]){body}(?![a-z0-9])", re.IGNORECASE)


def find_additive_match(
    text: str,
    aliases: tuple[str, ...],
    additive: str = "RED3",
) -> AliasMatch | None:
    """Detect additive in ingredient text, returning the earliest valid match span."""
    if not text or not text.strip():
        return None

    candidates: list[AliasMatch] = []

    if additive.upper() == "RED3" or any("red" in a.lower() or "erythrosine" in a.lower() for a in aliases):
        for canonical, pat in _RED3_PATTERNS:
            for m in pat.finditer(text):
                s, e = m.start(), m.end()
                if not _overlaps_decoy(text, s, e):
                    candidates.append(
                        AliasMatch(
                            additive=additive,
                            canonical_alias=canonical,
                            match_text=text[s:e],
                            start=s,
                            end=e,
                        )
                    )

    for alias in aliases:
        pat = _build_dynamic_alias_pattern(alias)
        for m in pat.finditer(text):
            s, e = m.start(), m.end()
            if not _overlaps_decoy(text, s, e):
                candidates.append(
                    AliasMatch(
                        additive=additive,
                        canonical_alias=alias,
                        match_text=text[s:e],
                        start=s,
                        end=e,
                    )
                )

    if not candidates:
        return None

    # Sort by earliest start, then longest span
    candidates.sort(key=lambda c: (c.start, -(c.end - c.start)))
    return candidates[0]


def is_unclear_or_generic_color(text: str) -> tuple[bool, str | None, int | None, int | None]:
    """Check if the ingredient list is unreadable or only declares generic artificial color."""
    if not text or not text.strip():
        return True, None, None, None

    stripped = text.strip()
    if len(stripped) < 3 or re.fullmatch(r"[\W_]+", stripped):
        return True, stripped, 0, len(text)

    for pat in _UNCLEAR_PATTERNS:
        m = pat.search(text)
        if m:
            return True, text[m.start():m.end()], m.start(), m.end()

    return False, None, None, None
