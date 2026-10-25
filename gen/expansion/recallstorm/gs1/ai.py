"""GS1 Application Identifier (AI 01, 10, 11, 17, 21) element string parser and builder."""
from __future__ import annotations

import calendar
import re
from datetime import date
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.gtin import is_valid_gtin, normalize_gtin

_AI_TABLE: dict[str, str] = {
    "01": "GTIN",
    "10": "BATCH_LOT",
    "11": "PROD_DATE",
    "17": "EXPIRY_DATE",
    "21": "SERIAL",
}

_PAREN_AI_RE = re.compile(r"\((\d{2,4})\)([^\(]+)")


def ai_table() -> dict[str, str]:
    """Return mapping of supported GS1 Application Identifier codes to names."""
    return dict(_AI_TABLE)


def _parse_gs1_yymmdd(yymmdd: str) -> date:
    if not isinstance(yymmdd, str) or not yymmdd.isdigit() or len(yymmdd) != 6:
        raise DataValidationError(f"GS1 date AI requires 6 digits YYMMDD, got: {yymmdd}")
    yy = int(yymmdd[0:2])
    mm = int(yymmdd[2:4])
    dd = int(yymmdd[4:6])
    year = 2000 + yy if yy < 50 else 1900 + yy
    if not (1 <= mm <= 12):
        raise DataValidationError(f"Invalid month in GS1 date: {yymmdd}")
    if dd == 0:
        dd = calendar.monthrange(year, mm)[1]
    return date(year, mm, dd)


def validate_ai(ai_code: str, value: str) -> bool:
    """Validate a single GS1 Application Identifier code and value."""
    if ai_code == "01":
        return len(value) == 14 and value.isdigit() and is_valid_gtin(value)
    if ai_code in ("11", "17"):
        try:
            _parse_gs1_yymmdd(value)
            return True
        except DataValidationError:
            return False
    if ai_code in ("10", "21"):
        return 1 <= len(value) <= 20
    return False


def parse_element_string(element_str: str) -> dict[str, str]:
    """Parse a bracketed or FNC1-delimited GS1 element string into an AI dict."""
    if not isinstance(element_str, str) or not element_str.strip():
        raise DataValidationError("GS1 element string must be non-empty")
    s = element_str.strip().removeprefix("]C1")
    if "(" in s:
        pairs = _PAREN_AI_RE.findall(s)
        if not pairs:
            raise DataValidationError(f"Malformed bracketed GS1 element string: {element_str}")
        out = {code: val.strip() for code, val in pairs}
        if "01" in out:
            out["01"] = normalize_gtin(out["01"])
        return out

    # Unbracketed fixed-length + GS (\x1d) parsing
    out = {}
    idx = 0
    while idx < len(s):
        if s[idx] == "\x1d":
            idx += 1
            continue
        code = s[idx:idx + 2]
        idx += 2
        if code == "01":
            out["01"] = s[idx:idx + 14]
            idx += 14
        elif code in ("11", "17"):
            out[code] = s[idx:idx + 6]
            idx += 6
        elif code in ("10", "21"):
            gs_pos = s.find("\x1d", idx)
            if gs_pos == -1:
                out[code] = s[idx:]
                break
            out[code] = s[idx:gs_pos]
            idx = gs_pos + 1
        else:
            raise DataValidationError(f"Unsupported unbracketed AI at {idx - 2}: {code}")
    return out


def ai_01(ais: dict[str, str]) -> str | None:
    """Return normalized 14-digit GTIN (AI 01) from parsed AI dict."""
    val = ais.get("01")
    return normalize_gtin(val) if val else None


def ai_10(ais: dict[str, str]) -> str | None:
    """Return batch/lot code (AI 10) from parsed AI dict."""
    return ais.get("10")


def ai_17(ais: dict[str, str]) -> date | None:
    """Return parsed expiration date (AI 17) from parsed AI dict."""
    val = ais.get("17")
    return _parse_gs1_yymmdd(val) if val else None


def ai_11(ais: dict[str, str]) -> date | None:
    """Return parsed production date (AI 11) from parsed AI dict."""
    val = ais.get("11")
    return _parse_gs1_yymmdd(val) if val else None


def ai_21(ais: dict[str, str]) -> str | None:
    """Return serial number (AI 21) from parsed AI dict."""
    return ais.get("21")


def build_element_string(ais: dict[str, str]) -> str:
    """Format an AI dictionary into a canonical bracketed GS1 element string."""
    if not isinstance(ais, dict) or not ais:
        raise DataValidationError("ais must be a non-empty dict")
    order = ["01", "11", "17", "10", "21"]
    parts: list[str] = []
    for k in order:
        if k in ais and ais[k] is not None:
            parts.append(f"({k}){ais[k]}")
    for k in sorted(ais.keys()):
        if k not in order and ais[k] is not None:
            parts.append(f"({k}){ais[k]}")
    return "".join(parts)
