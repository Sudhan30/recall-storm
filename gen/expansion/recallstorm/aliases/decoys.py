"""Decoy and near-miss pattern detection (Red 40, D&C Red 33, Red #30, '3 red peppers', etc.)."""
from __future__ import annotations

import re

DECOY_PATTERNS: tuple[str, ...] = (
    r"\b(?:FD&C\s+)?RED\s*(?:NO\.?\s*|#)?\s*40(?:\s+LAKE)?\b",
    r"\b(?:FD&C\s+|D&C\s+)?RED\s*(?:NO\.?\s*|#)?\s*(?:28|30|33|36)\b",
    r"\b3\s+RED\s+(?:BELL\s+)?PEPPERS?\b",
    r"\b3\s+PEPPER\b",
    r"\bRED\s+3\s+(?:BELL\s+)?PEPPERS?\b",
    r"\bRED\s+PEPPER\b",
    r"\bRED\s+BEET\b",
    r"\bRED\s+CABBAGE\b",
    r"\bRED\s+RADISH\b",
    r"\bCARMINE\b",
    r"\bANNATTO\b",
    r"\bLYCOPENE\b",
)


def is_red40(text: str, pos: int = 0) -> bool:
    """Return True if text at or near pos is a Red 40 or Red 40 Lake mention."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    window = text[max(0, pos - 10):pos + 30]
    return bool(re.search(r"RED\s*(?:DYE\s*)?(?:NO\.?\s*|#)?\s*40\b", window, re.IGNORECASE))


def is_dc_red_33(text: str, pos: int = 0) -> bool:
    """Return True if text at or near pos is D&C Red 33 / Red 30 / Red 28."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    window = text[max(0, pos - 10):pos + 30]
    return bool(re.search(r"RED\s*(?:DYE\s*)?(?:NO\.?\s*|#)?\s*(?:28|30|33|36)\b", window, re.IGNORECASE))


def is_quantity_phrase(text: str, start: int, end: int) -> bool:
    """Return True if a match is actually a food quantity phrase like '3 red bell peppers' or 'red 3 peppers'."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    after = text[end:end + 25]
    before = text[max(0, start - 15):start]
    if re.match(r"^\s*(?:bell\s+|chili\s+|jalapeno\s+)?(?:peppers?|apples?|cherries|berries|beans|chili|onions?)\b", after, re.IGNORECASE):
        return True
    if re.search(r"\b(?:contains|blend\s+of|with)\s+$", before, re.IGNORECASE) and re.match(r"^\s*peppers?\b", after, re.IGNORECASE):
        return True
    snippet = text[max(0, start - 5):min(len(text), end + 20)]
    if re.search(r"\b3\s+red\s+(?:bell\s+)?peppers?\b", snippet, re.IGNORECASE):
        return True
    return False


def is_product_name_phrase(text: str, start: int, end: int) -> bool:
    """Return True if the match is part of a non-dye botanical or spice phrase."""
    after = text[end:end + 20]
    return bool(re.match(r"^\s*(?:bean|lentil|quinoa|vinegar|wine|potato)\b", after, re.IGNORECASE))


def is_lake_pigment(text: str, start: int, end: int) -> bool:
    """Return True if the matched dye is followed by 'LAKE' (e.g., FD&C Red #3 Lake vs Red #40 Lake)."""
    after = text[end:end + 10]
    return bool(re.match(r"^\s*LAKE\b", after, re.IGNORECASE))


def decoy_examples() -> list[str]:
    """Return canonical decoy ingredient phrases for testing."""
    return [
        "FD&C RED #40",
        "RED 40 LAKE",
        "D&C RED #33",
        "RED #30",
        "3 RED BELL PEPPERS",
        "COLORED RED WITH CARMINE",
    ]


def classify_red_mention(text: str) -> str:
    """Classify a 'Red' mention into RED3, RED40, DC_RED, NATURAL_RED, or NONE."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if re.search(r"\b(?:FD&C\s+)?RED\s*(?:DYE\s*)?(?:NO\.?\s*|#)?\s*0?3\b(?!\d)", text, re.IGNORECASE):
        if not re.search(r"\b3\s+RED\s+(?:BELL\s+)?PEPPERS?\b", text, re.IGNORECASE):
            return "RED3"
    if re.search(r"\bRED\s*(?:NO\.?\s*|#)?\s*40\b", text, re.IGNORECASE):
        return "RED40"
    if re.search(r"\bRED\s*(?:NO\.?\s*|#)?\s*(?:28|30|33)\b", text, re.IGNORECASE):
        return "DC_RED"
    if re.search(r"\b(?:CARMINE|BEET|ANNATTO|RED\s+PEPPER)\b", text, re.IGNORECASE):
        return "NATURAL_RED"
    return "NONE"


def near_miss_report(text: str) -> list[dict]:
    """Find all decoy / near-miss patterns present in an ingredient string."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    out: list[dict] = []
    for pat in DECOY_PATTERNS:
        for m in re.finditer(pat, text, re.IGNORECASE):
            out.append({"match": m.group(0), "start": m.start(), "end": m.end()})
    return out
