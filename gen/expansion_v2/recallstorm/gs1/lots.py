"""Lot code normalization, range matching, and expiry window checks."""
from __future__ import annotations

from datetime import date
import fnmatch
import re

_PREFIX_NOISE_RE = re.compile(r"^(?:LOT|BATCH|CODE|L)[#:\-\s]+", re.IGNORECASE)
_RANGE_TEXT_RE = re.compile(r"\b([A-Z0-9]{3,16})\s*(?:to|through|-)\s*([A-Z0-9]{3,16})\b", re.IGNORECASE)


def normalize_lot(lot: str) -> str:
    """Normalize a lot string by stripping 'LOT:' prefixes, spaces, and hyphens, in uppercase."""
    if not isinstance(lot, str):
        raise TypeError("lot must be a string")
    cleaned = _PREFIX_NOISE_RE.sub("", lot.strip())
    return re.sub(r"[\s\-]+", "", cleaned).upper()


def parse_lot_code(raw: str) -> str:
    """Parse and normalize a raw lot code string."""
    norm = normalize_lot(raw)
    if not norm:
        raise ValueError(f"Empty lot code: {raw!r}")
    return norm


def lot_in_range(lot: str, start_lot: str, end_lot: str) -> bool:
    """Return True if normalized lot falls lexicographically/numerically within [start_lot, end_lot]."""
    target = normalize_lot(lot)
    lo = normalize_lot(start_lot)
    hi = normalize_lot(end_lot)
    if not target or not lo or not hi:
        return False
    if len(target) == len(lo) == len(hi):
        return lo <= target <= hi
    # Split alpha prefix + numeric suffix if present
    m_t = re.match(r"^([A-Z]*)(\d+)([A-Z]*)$", target)
    m_lo = re.match(r"^([A-Z]*)(\d+)([A-Z]*)$", lo)
    m_hi = re.match(r"^([A-Z]*)(\d+)([A-Z]*)$", hi)
    if m_t and m_lo and m_hi and m_t.group(1) == m_lo.group(1) == m_hi.group(1):
        return (int(m_lo.group(2)), m_lo.group(3)) <= (int(m_t.group(2)), m_t.group(3)) <= (int(m_hi.group(2)), m_hi.group(3))
    return lo <= target <= hi


def lot_range_from_text(text: str) -> list[tuple[str, str]]:
    """Extract (start_lot, end_lot) pairs from recall code_info text."""
    if not isinstance(text, str):
        return []
    return [(normalize_lot(m.group(1)), normalize_lot(m.group(2))) for m in _RANGE_TEXT_RE.finditer(text)]


def lot_pattern(pattern: str) -> re.Pattern:
    """Compile a wildcard glob pattern (e.g. 'L26*') into a case-insensitive regex."""
    norm_pat = _PREFIX_NOISE_RE.sub("", pattern.strip()).upper()
    return re.compile(fnmatch.translate(norm_pat), re.IGNORECASE)


def lot_matches_recall(lot: str, recall_lots: list[str]) -> bool:
    """Return True if lot matches any exact code, glob pattern ('*'), or range ('A..B') in recall_lots."""
    target = normalize_lot(lot)
    if not target:
        return False
    for pat in recall_lots:
        s = pat.strip()
        if ".." in s:
            a, b = s.split("..", 1)
            if lot_in_range(target, a, b):
                return True
        elif "-" in s and not s.upper().startswith("LOT"):
            a, b = s.split("-", 1)
            if normalize_lot(s) == target or lot_in_range(target, a, b):
                return True
        elif "*" in s or "?" in s:
            if lot_pattern(s).match(target):
                return True
        elif normalize_lot(s) == target:
            return True
    return False


def recall_lot_filter(lots: list[str], recall_lots: list[str]) -> list[str]:
    """Filter a list of lot codes to those matching recall_lots."""
    return [l for l in lots if lot_matches_recall(l, recall_lots)]


def expiry_in_range(exp: date, start: date, end: date) -> bool:
    """Return True if exp is inclusively within [start, end]."""
    return start <= exp <= end


def date_range_overlap(r1: tuple[date, date], r2: tuple[date, date]) -> bool:
    """Return True if two inclusive date ranges [s1, e1] and [s2, e2] overlap."""
    return max(r1[0], r2[0]) <= min(r1[1], r2[1])
