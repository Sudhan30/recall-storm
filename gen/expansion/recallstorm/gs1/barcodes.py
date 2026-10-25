"""Retail barcode scanner string parsing (UPC-A, EAN-13, ITF-14, variable measure)."""
from __future__ import annotations

from dataclasses import dataclass
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.gtin import (
    gtin12_to_14,
    gtin13_to_14,
    gtin_check_digit,
    is_valid_gtin,
    normalize_gtin,
)


@dataclass(frozen=True)
class ScanResult:
    """Parsed barcode scan result."""

    raw: str
    gtin14: str
    symbology: str
    is_variable: bool = False


def upc_a_to_gtin(upc: str) -> str:
    """Convert a 12-digit UPC-A string to GTIN-14."""
    return gtin12_to_14(upc)


def ean13_to_gtin(ean: str) -> str:
    """Convert a 13-digit EAN-13 string to GTIN-14."""
    return gtin13_to_14(ean)


def is_variable_measure(code: str) -> bool:
    """Return True if a 12-or-14 digit code is a variable-measure price-embedded item (prefix '2' or '02')."""
    if not isinstance(code, str):
        return False
    norm = "".join(c for c in code.strip() if c.isdigit()).zfill(14)
    return norm.startswith("002")


def strip_price_embedded(code: str) -> str:
    """Zero out the 5-digit price field in a variable-measure UPC and recompute the check digit."""
    norm = normalize_gtin(code)
    if not is_variable_measure(norm):
        return norm
    # Keep indicator + prefix + item (first 8 digits of GTIN-14), zero price digits 8..13
    payload = norm[:8] + "00000"
    chk = gtin_check_digit(payload)
    return payload + str(chk)


def barcode_type(code: str) -> str:
    """Identify the barcode symbology (GTIN-8, UPC-A, EAN-13, GTIN-14, GS1-128)."""
    if not isinstance(code, str) or not code.strip():
        raise DataValidationError("Barcode string is empty")
    s = code.strip()
    if s.startswith("(") or "]C1" in s:
        return "GS1-128"
    if not s.isdigit():
        raise DataValidationError(f"Non-numeric barcode: {s}")
    n = len(s)
    if n == 8:
        return "EAN-8"
    if n == 12:
        return "UPC-A"
    if n == 13:
        return "EAN-13"
    if n == 14:
        return "ITF-14"
    raise DataValidationError(f"Unsupported barcode length: {n}")


def scan_to_gtin(scan: str) -> str:
    """Extract normalized 14-digit GTIN from a scanner string."""
    if not isinstance(scan, str) or not scan.strip():
        raise DataValidationError("Empty scan string")
    s = scan.strip().removeprefix("]C1").strip()
    if s.startswith("(01)") and len(s) >= 18:
        return normalize_gtin(s[4:18])
    return normalize_gtin(s)


def parse_scan_string(scan: str) -> ScanResult:
    """Parse a raw barcode scanner string into a ScanResult."""
    sym = barcode_type(scan)
    gtin14 = scan_to_gtin(scan)
    return ScanResult(raw=scan.strip(), gtin14=gtin14, symbology=sym, is_variable=is_variable_measure(gtin14))


def validate_scan(scan: str) -> bool:
    """Return True if scan string has a valid GTIN check digit."""
    try:
        g = scan_to_gtin(scan)
        return is_valid_gtin(g)
    except DataValidationError:
        return False
