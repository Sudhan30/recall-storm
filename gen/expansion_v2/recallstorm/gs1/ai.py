"""GS1 Application Identifiers (AI 01, 10, 11, 17, 21) parsing and formatting."""
from __future__ import annotations

import calendar
from datetime import date
import re

from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.gtin import is_valid_gtin, normalize_gtin

_AI_TABLE: dict[str, str] = {
    "01": "GTIN",
    "10": "BATCH_LOT",
    "11": "PROD_DATE",
    "17": "EXPIRY",
    "21": "SERIAL",
}

_PAREN_RE = re.compile(r"\((\d{2,4})\)([^(]+)")


def ai_table() -> dict[str, str]:
    """Return mapping of supported GS1 Application Identifier codes to names."""
    return dict(_AI_TABLE)


def _parse_gs1_date(yymmdd: str) -> date:
    if not isinstance(yymmdd, str) or len(yymmdd) != 6 or not yymmdd.isdigit():
        raise DataValidationError(f"Invalid GS1 YYMMDD date: {yymmdd!r}")
    yy = int(yymmdd[0:2])
    mm = int(yymmdd[2:4])
    dd = int(yymmdd[4:6])
    year = 2000 + yy if yy < 80 else 1900 + yy
    if not (1 <= mm <= 12):
        raise DataValidationError(f"Invalid month in GS1 date: {yymmdd!r}")
    if dd == 0:
        dd = calendar.monthrange(year, mm)[1]
    return date(year, mm, dd)


def parse_element_string(s: str) -> dict[str, str]:
    """Parse a GS1 element string (parenthesized or FNC1/fixed-length) into AI -> value."""
    if not isinstance(s, str) or not s.strip():
        raise DataValidationError("Empty GS1 element string")
    text = s.strip()
    for sym in ("]C1", "]d2", "]Q3"):
        if text.startswith(sym):
            text = text[len(sym) :]

    if "(" in text and ")" in text:
        out = {m.group(1): m.group(2).strip() for m in _PAREN_RE.finditer(text)}
        if not out:
            raise DataValidationError(f"Malformed parenthesized element string: {s!r}")
        return out

    # Unparenthesized fixed/variable parsing with GS (\x1d)
    out: dict[str, str] = {}
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "\x1d":
            i += 1
            continue
        ai = text[i : i + 2]
        i += 2
        if ai == "01":
            out["01"] = text[i : i + 14]
            i += 14
        elif ai in {"11", "17"}:
            out[ai] = text[i : i + 6]
            i += 6
        elif ai in {"10", "21"}:
            gs_pos = text.find("\x1d", i)
            if gs_pos == -1:
                out[ai] = text[i:]
                break
            out[ai] = text[i:gs_pos]
            i = gs_pos + 1
        else:
            raise DataValidationError(f"Unsupported unparenthesized AI {ai!r} in {s!r}")
    return out


def ai_01(ais: dict[str, str]) -> str | None:
    """Extract normalized 14-digit GTIN from AI 01."""
    return normalize_gtin(ais["01"]) if "01" in ais else None


def ai_10(ais: dict[str, str]) -> str | None:
    """Extract batch/lot code from AI 10."""
    return ais.get("10")


def ai_17(ais: dict[str, str]) -> date | None:
    """Extract expiration date from AI 17 (YYMMDD, where DD=00 means end of month)."""
    return _parse_gs1_date(ais["17"]) if "17" in ais else None


def ai_11(ais: dict[str, str]) -> date | None:
    """Extract production date from AI 11 (YYMMDD)."""
    return _parse_gs1_date(ais["11"]) if "11" in ais else None


def ai_21(ais: dict[str, str]) -> str | None:
    """Extract serial number from AI 21."""
    return ais.get("21")


def validate_ai(code: str, val: str) -> bool:
    """Validate a single GS1 AI code and value."""
    if code == "01":
        return len(val) == 14 and is_valid_gtin(val)
    if code in {"11", "17"}:
        try:
            _parse_gs1_date(val)
            return True
        except DataValidationError:
            return False
    if code in {"10", "21"}:
        return 1 <= len(val) <= 20
    return False


def build_element_string(ais: dict[str, str]) -> str:
    """Format an AI dictionary into canonical human-readable parenthesized GS1 element string."""
    order = ["01", "17", "11", "10", "21"]
    parts: list[str] = []
    for k in order:
        if k in ais and ais[k] is not None:
            val = normalize_gtin(ais[k]) if k == "01" else str(ais[k])
            parts.append(f"({k}){val}")
    for k in sorted(ais.keys()):
        if k not in order and ais[k] is not None:
            parts.append(f"({k}){ais[k]}")
    return "".join(parts)
