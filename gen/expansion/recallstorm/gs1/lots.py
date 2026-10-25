"""Lot code normalization, lexicographic/numeric range matching, and expiry date overlap."""
from __future__ import annotations

import re
from datetime import date
from recallstorm.core.errors import DataValidationError

_LOT_RANGE_RE = re.compile(r"\b([A-Z0-9]{3,16})\s*(?:through|to|-)\s*([A-Z0-9]{3,16})\b", re.IGNORECASE)


def normalize_lot(lot: str) -> str:
    """Normalize a lot/batch code by stripping punctuation/spaces and uppercasing."""
    if not isinstance(lot, str) or not lot.strip():
        raise DataValidationError("Lot code must be a non-empty string")
    cleaned = re.sub(r"[^A-Za-z0-9]", "", lot.strip()).upper()
    if not cleaned:
        raise DataValidationError(f"Lot code contains no alphanumeric characters: {lot}")
    return cleaned


def parse_lot_code(raw: str) -> str:
    """Strip 'LOT', 'BATCH', or '#' prefixes and normalize a lot code."""
    if not isinstance(raw, str) or not raw.strip():
        raise DataValidationError("raw lot string must be non-empty")
    s = re.sub(r"^(?:LOT|BATCH|CODE)[#:\s\-]*", "", raw.strip(), flags=re.IGNORECASE)
    return normalize_lot(s)


def lot_pattern(lot: str) -> str:
    """Return the structural pattern of a lot code ('A' for alpha, '9' for digit)."""
    norm = normalize_lot(lot)
    return "".join("A" if ch.isalpha() else "9" for ch in norm)


def lot_in_range(lot: str, start_lot: str, end_lot: str) -> bool:
    """Return True if lot falls inclusively within [start_lot, end_lot] of matching prefix/length."""
    l_norm = normalize_lot(lot)
    s_norm = normalize_lot(start_lot)
    e_norm = normalize_lot(end_lot)
    if len(l_norm) != len(s_norm) or len(l_norm) != len(e_norm):
        return False
    return s_norm <= l_norm <= e_norm


def lot_range_from_text(text: str) -> list[tuple[str, str]]:
    """Extract (start_lot, end_lot) pairs from recall notice text."""
    if not isinstance(text, str):
        return []
    out: list[tuple[str, str]] = []
    for a, b in _LOT_RANGE_RE.findall(text):
        na, nb = normalize_lot(a), normalize_lot(b)
        if len(na) == len(nb) and na <= nb:
            out.append((na, nb))
    return out


def lot_matches_recall(
    lot: str,
    recall_lots: list[str] | tuple[str, ...],
    recall_ranges: list[tuple[str, str]] | None = None,
) -> bool:
    """Return True if lot matches any explicit recall lot (supports '*' wildcard) or lot range."""
    l_norm = normalize_lot(lot)
    for rl in recall_lots:
        if "*" in rl:
            pat = "^" + re.escape(rl.strip().upper()).replace(r"\*", ".*") + "$"
            if re.match(pat, l_norm):
                return True
        elif normalize_lot(rl) == l_norm:
            return True
    for s_lot, e_lot in recall_ranges or []:
        if lot_in_range(l_norm, s_lot, e_lot):
            return True
    return False


def expiry_in_range(exp: date | str, start_date: date | str, end_date: date | str) -> bool:
    """Return True if expiry date falls inclusively within [start_date, end_date]."""
    d = date.fromisoformat(exp) if isinstance(exp, str) else exp
    s = date.fromisoformat(start_date) if isinstance(start_date, str) else start_date
    e = date.fromisoformat(end_date) if isinstance(end_date, str) else end_date
    if e < s:
        raise ValueError("end_date cannot precede start_date")
    return s <= d <= e


def date_range_overlap(r1: tuple[date | str, date | str], r2: tuple[date | str, date | str]) -> bool:
    """Return True if two inclusive date ranges [s1, e1] and [s2, e2] overlap."""
    s1 = date.fromisoformat(r1[0]) if isinstance(r1[0], str) else r1[0]
    e1 = date.fromisoformat(r1[1]) if isinstance(r1[1], str) else r1[1]
    s2 = date.fromisoformat(r2[0]) if isinstance(r2[0], str) else r2[0]
    e2 = date.fromisoformat(r2[1]) if isinstance(r2[1], str) else r2[1]
    return max(s1, s2) <= min(e1, e2)


def recall_lot_filter(items: list[dict], recall_lots: list[str]) -> list[dict]:
    """Filter inventory item dicts whose 'lot' matches recall_lots."""
    return [it for it in items if it.get("lot") and lot_matches_recall(str(it["lot"]), recall_lots)]
