"""UPC-A, EAN-13, and variable-measure barcode parsing."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.gtin import gtin12_to_14, gtin13_to_14, gtin_check_digit, is_valid_gtin, normalize_gtin


@dataclass(frozen=True)
class ScanResult:
    """Result of parsing a POS or handheld barcode scan."""

    raw: str
    gtin14: str
    kind: str
    is_variable: bool


def upc_a_to_gtin(upc: str) -> str:
    """Convert a 12-digit UPC-A string to GTIN-14."""
    return gtin12_to_14(upc)


def ean13_to_gtin(ean: str) -> str:
    """Convert a 13-digit EAN-13 string to GTIN-14."""
    return gtin13_to_14(ean)


def is_variable_measure(code: str) -> bool:
    """Return True if a 12-digit UPC or 14-digit GTIN is a Prefix-2 variable-measure item."""
    digits = "".join(c for c in str(code) if c.isdigit())
    if len(digits) == 12:
        return digits.startswith("2")
    if len(digits) == 14:
        return digits.startswith("002")
    return False


def strip_price_embedded(code: str) -> str:
    """Zero out the 5-digit price/weight field in a Prefix-2 variable-measure UPC and recalculate check digit."""
    digits = "".join(c for c in str(code) if c.isdigit())
    if len(digits) == 14 and digits.startswith("002"):
        digits = digits[2:]
    if len(digits) != 12 or not digits.startswith("2"):
        return normalize_gtin(digits)
    base11 = digits[:6] + "00000"
    chk = gtin_check_digit(base11)
    return f"00{base11}{chk}"


def barcode_type(code: str) -> str:
    """Return the symbology/format name ('GTIN-8', 'UPC-A', 'EAN-13', 'GTIN-14', or 'UNKNOWN')."""
    digits = "".join(c for c in str(code) if c.isdigit())
    mapping = {8: "GTIN-8", 12: "UPC-A", 13: "EAN-13", 14: "GTIN-14"}
    return mapping.get(len(digits), "UNKNOWN")


def validate_scan(scan: str) -> bool:
    """Return True if scan contains a valid GTIN check digit."""
    digits = "".join(c for c in str(scan) if c.isdigit())
    return is_valid_gtin(digits)


def scan_to_gtin(scan: str) -> str:
    """Normalize a scanned barcode string to a 14-digit GTIN."""
    s = (scan or "").strip()
    for prefix in ("]C1", "]e0", "]E0", "]d2"):
        if s.startswith(prefix):
            s = s[len(prefix) :]
    digits = "".join(c for c in s if c.isdigit())
    if len(digits) >= 16 and digits.startswith("01"):
        digits = digits[2:16]
    if len(digits) not in {8, 12, 13, 14}:
        raise DataValidationError(f"Cannot extract GTIN from scan: {scan!r}")
    return normalize_gtin(digits)


def parse_scan_string(scan: str) -> ScanResult:
    """Parse a raw scanner string into a ScanResult."""
    g14 = scan_to_gtin(scan)
    return ScanResult(raw=scan, gtin14=g14, kind=barcode_type(scan), is_variable=is_variable_measure(g14))
