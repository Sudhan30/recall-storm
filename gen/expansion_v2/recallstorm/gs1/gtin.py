"""GTIN check digit calculation, validation, and normalization to GTIN-14."""
from __future__ import annotations

from recallstorm.core.errors import DataValidationError


def gtin_check_digit(digits_without_check: str) -> int:
    """Compute the GS1 Mod-10 check digit for a 7, 11, 12, 13, or 17 digit payload."""
    if not isinstance(digits_without_check, str) or not digits_without_check.isdigit():
        raise DataValidationError("GTIN payload must be numeric digits")
    if len(digits_without_check) not in {7, 11, 12, 13, 17}:
        raise DataValidationError(f"Unsupported GS1 payload length: {len(digits_without_check)}")
    total = 0
    for idx, ch in enumerate(reversed(digits_without_check)):
        weight = 3 if idx % 2 == 0 else 1
        total += int(ch) * weight
    return (10 - (total % 10)) % 10


def is_valid_gtin(gtin: str) -> bool:
    """Return True if gtin is a valid 8, 12, 13, or 14 digit GTIN with a valid GS1 check digit."""
    if not isinstance(gtin, str) or not gtin.isdigit():
        return False
    if len(gtin) not in {8, 12, 13, 14}:
        return False
    return gtin_check_digit(gtin[:-1]) == int(gtin[-1])


def gtin8_to_14(gtin8: str) -> str:
    """Pad a GTIN-8 to GTIN-14."""
    if not isinstance(gtin8, str) or len(gtin8) != 8 or not gtin8.isdigit():
        raise DataValidationError("Invalid GTIN-8")
    return gtin8.zfill(14)


def gtin12_to_14(gtin12: str) -> str:
    """Pad a 12-digit UPC-A (GTIN-12) to GTIN-14."""
    if not isinstance(gtin12, str) or len(gtin12) != 12 or not gtin12.isdigit():
        raise DataValidationError("Invalid GTIN-12")
    return gtin12.zfill(14)


def gtin13_to_14(gtin13: str) -> str:
    """Pad a 13-digit EAN-13 (GTIN-13) to GTIN-14."""
    if not isinstance(gtin13, str) or len(gtin13) != 13 or not gtin13.isdigit():
        raise DataValidationError("Invalid GTIN-13")
    return gtin13.zfill(14)


def normalize_gtin(gtin: str) -> str:
    """Normalize an 8, 12, 13, or 14 digit GTIN string to 14 digits."""
    if not isinstance(gtin, str):
        raise DataValidationError("GTIN must be a string")
    digits = "".join(c for c in gtin.strip() if c.isdigit())
    if len(digits) not in {8, 12, 13, 14}:
        raise DataValidationError(f"GTIN must have 8, 12, 13, or 14 digits, got {gtin!r}")
    return digits.zfill(14)


def gtin_indicator(gtin14: str) -> str:
    """Return the 1-digit packaging indicator of a GTIN-14."""
    norm = normalize_gtin(gtin14)
    return norm[0]


def gtin_company_prefix(gtin: str, length: int = 7) -> str:
    """Extract the GS1 company prefix (starting after indicator digit) from a GTIN."""
    norm = normalize_gtin(gtin)
    return norm[1 : 1 + length]


def gtin_variants(gtin: str) -> tuple[str, ...]:
    """Return (GTIN-14, GTIN-13, GTIN-12) representations of a GTIN."""
    norm = normalize_gtin(gtin)
    return (norm, norm[1:], norm[2:])
