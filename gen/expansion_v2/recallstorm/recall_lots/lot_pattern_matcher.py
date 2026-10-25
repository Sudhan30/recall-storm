"""Wildcard, Julian date, plant-line-shift, and OCR-tolerant lot matching."""
from __future__ import annotations

from dataclasses import dataclass
import fnmatch
import re

from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.lots import lot_in_range, normalize_lot


@dataclass(frozen=True)
class LotPatternSpec:
    """Specification for a recall lot pattern."""

    ref_id: str = "LOT-PAT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class WildcardLotMatcher:
    """Wildcard glob matcher for recalled lot codes."""

    ref_id: str = "LOT-GLOB-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def compile_lot_glob_expression(glob_pat: str) -> re.Pattern:
    """Compile a wildcard glob expression into a regex."""
    _req(glob_pat, "glob_pat")
    return re.compile(fnmatch.translate(str(glob_pat).strip().upper()), re.IGNORECASE)


def match_alphanumeric_lot_range(lot: str, start_lot: str, end_lot: str) -> bool:
    """Return True if lot falls within [start_lot, end_lot]."""
    _req(lot, "lot")
    return lot_in_range(str(lot), str(start_lot), str(end_lot))


def strip_lot_prefix_noise(raw_lot: str) -> str:
    """Strip 'LOT:', 'BATCH#', spaces, and punctuation noise from raw_lot."""
    _req(raw_lot, "raw_lot")
    return normalize_lot(str(raw_lot))


def evaluate_julian_date_lot(julian_code: str, start_ddd: int = 1, end_ddd: int = 366) -> dict:
    """Evaluate a YYDDD or DDD Julian date lot code against [start_ddd, end_ddd]."""
    _req(julian_code, "julian_code")
    digits = "".join(c for c in str(julian_code) if c.isdigit())
    if len(digits) < 3:
        raise DataValidationError("Julian code requires at least 3 digits")
    ddd = int(digits[-3:])
    return {"op": "evaluate_julian_date_lot", "day_of_year": ddd, "in_range": start_ddd <= ddd <= end_ddd, "src": "recallstorm/recall_lots/lot_pattern_matcher.py"}


def parse_plant_line_shift_code(code: str) -> dict:
    """Parse a structured plant-line-shift lot code (e.g. 'P02-L4-S1')."""
    _req(code, "code")
    parts = str(code).upper().split("-")
    return {
        "op": "parse_plant_line_shift_code",
        "plant": parts[0] if parts else "P01",
        "line": parts[1] if len(parts) > 1 else "L1",
        "shift": parts[2] if len(parts) > 2 else "S1",
        "src": "recallstorm/recall_lots/lot_pattern_matcher.py",
    }


def match_embossed_can_code(can_code: str, target_prefix: str) -> bool:
    """Match an embossed metal can lid code against target_prefix."""
    _req(can_code, "can_code")
    _req(target_prefix, "target_prefix")
    return normalize_lot(can_code).startswith(normalize_lot(target_prefix))


def handle_ocr_confused_characters(raw_lot: str) -> str:
    """Normalize OCR-confused characters (O->0, I/l->1, Z->2) in numeric position of lot codes."""
    _req(raw_lot, "raw_lot")
    trans = str.maketrans({"O": "0", "I": "1", "Z": "2"})
    return str(raw_lot).upper().translate(trans)


def score_lot_string_similarity(lot1: str, lot2: str) -> float:
    """Compute character overlap similarity in [0.0, 1.0] between two lot codes."""
    _req(lot1, "lot1")
    _req(lot2, "lot2")
    a, b = normalize_lot(lot1), normalize_lot(lot2)
    if a == b:
        return 1.0
    matches = sum(1 for x, y in zip(a, b) if x == y)
    return round(matches / max(len(a), len(b), 1), 4)


def expand_hyphenated_lot_span(prefix: str, start_num: int, end_num: int) -> list[str]:
    """Expand a numeric lot span (e.g. 'L', 10, 12 -> ['L10', 'L11', 'L12'])."""
    _req(prefix, "prefix")
    if start_num < 0 or end_num < start_num or (end_num - start_num) > 500:
        raise DataValidationError("Invalid lot span")
    return [f"{prefix}{i}" for i in range(start_num, end_num + 1)]


def validate_lot_against_regex_bank(lot: str, patterns: list[str]) -> bool:
    """Return True if lot matches any regex in patterns."""
    _req(lot, "lot")
    return any(bool(re.search(p, str(lot), re.IGNORECASE)) for p in patterns)
