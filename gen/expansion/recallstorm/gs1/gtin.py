"""GS1 GTIN-8/12/13/14 modulo-10 check digit calculation and normalization."""
from __future__ import annotations

from recallstorm.core.errors import DataValidationError


def gtin_check_digit(digits_without_check: str) -> int:
    """Compute the GS1 Modulo-10 check digit for a 7, 11, 12, or 13 digit payload."""
    if not isinstance(digits_without_check, str) or not digits_without_check.isdigit():
        raise DataValidationError("digits_without_check must be a numeric string")
    if len(digits_without_check) not in (7, 11, 12, 13):
        raise DataValidationError(f"Invalid payload length for GTIN check digit: {len(digits_without_check)}")
    total = 0
    for idx, ch in enumerate(reversed(digits_without_check)):
        weight = 3 if idx % 2 == 0 else 1
        total += int(ch) * weight
    return (10 - (total % 10)) % 10


def is_valid_gtin(code: str) -> bool:
    """Return True if code is a valid 8, 12, 13, or 14 digit GTIN with a valid GS1 check digit."""
    if not isinstance(code, str):
        return False
    s = code.strip()
    if not s.isdigit() or len(s) not in (8, 12, 13, 14):
        return False
    expected = gtin_check_digit(s[:-1])
    return int(s[-1]) == expected


def gtin8_to_14(code: str) -> str:
    """Convert an 8-digit GTIN-8 to a 14-digit GTIN-14."""
    if not isinstance(code, str) or not code.strip().isdigit() or len(code.strip()) != 8:
        raise DataValidationError("Expected 8-digit GTIN-8")
    return code.strip().zfill(14)


def gtin12_to_14(code: str) -> str:
    """Convert a 12-digit UPC-A / GTIN-12 to a 14-digit GTIN-14."""
    if not isinstance(code, str) or not code.strip().isdigit() or len(code.strip()) != 12:
        raise DataValidationError("Expected 12-digit GTIN-12")
    return code.strip().zfill(14)


def gtin13_to_14(code: str) -> str:
    """Convert a 13-digit EAN-13 / GTIN-13 to a 14-digit GTIN-14."""
    if not isinstance(code, str) or not code.strip().isdigit() or len(code.strip()) != 13:
        raise DataValidationError("Expected 13-digit GTIN-13")
    return code.strip().zfill(14)


def normalize_gtin(code: str) -> str:
    """Normalize an 8, 12, 13, or 14 digit GTIN string to 14 digits."""
    if not isinstance(code, str) or not code.strip():
        raise DataValidationError("GTIN code must be a non-empty string")
    digits = "".join(ch for ch in code.strip() if ch.isdigit())
    if len(digits) not in (8, 12, 13, 14):
        raise DataValidationError(f"GTIN must have 8, 12, 13, or 14 digits, got {len(digits)}")
    return digits.zfill(14)


def gtin_indicator(gtin14: str) -> str:
    """Return the 1st digit (packaging indicator) of a normalized GTIN-14."""
    norm = normalize_gtin(gtin14)
    return norm[0]


def gtin_company_prefix(gtin14: str) -> str:
    """Return the GS1 company prefix slice (digits 1..8) of a normalized GTIN-14."""
    norm = normalize_gtin(gtin14)
    return norm[1:8]


def gtin_variants(code: str) -> list[str]:
    """Return equivalent GTIN-14, GTIN-13, and GTIN-12 representations for lookup."""
    norm = normalize_gtin(code)
    variants = [norm]
    if norm.startswith("0") and norm[1:] not in variants:
        variants.append(norm[1:])
    if norm.startswith("00") and norm[2:] not in variants:
        variants.append(norm[2:])
    return variants
