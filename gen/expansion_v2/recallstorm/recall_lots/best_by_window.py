"""Parse Best-By, Use-By, and Julian expiration stamps into calendar windows."""
from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
import re

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class DateWindowSpec:
    """Inclusive calendar date window for recalled Best-By stamps."""

    ref_id: str = "BB-WIN-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ExpirationFormatParser:
    """Parser for inkjet Best-By / Use-By package date stamps."""

    ref_id: str = "BB-FMT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def normalize_two_digit_year(yy: int) -> int:
    """Convert a 2-digit year (00-99) to a 4-digit year (2000-2079 or 1980-1999)."""
    if not isinstance(yy, int) or not (0 <= yy <= 99):
        raise DataValidationError("yy must be in 0..99")
    return 2000 + yy if yy < 80 else 1900 + yy


def parse_stamped_date_string(stamp: str) -> str:
    """Parse an inkjet stamp like '2026-08-15' or '08/15/26' into ISO 'YYYY-MM-DD'."""
    _req(stamp, "stamp")
    s = str(stamp).strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    m = re.match(r"^(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})$", s)
    if m:
        mm, dd, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if yr < 100:
            yr = normalize_two_digit_year(yr)
        return date(yr, mm, dd).isoformat()
    raise DataValidationError(f"Unrecognized date stamp: {stamp!r}")


def evaluate_inclusive_date_range(target_iso: str, start_iso: str, end_iso: str) -> bool:
    """Return True if target_iso is inclusively within [start_iso, end_iso]."""
    _req(target_iso, "target_iso")
    return str(start_iso) <= str(target_iso) <= str(end_iso)


def convert_julian_to_calendar_date(year: int, day_of_year: int) -> str:
    """Convert (year, day_of_year 1..366) to ISO 'YYYY-MM-DD'."""
    if not (1 <= day_of_year <= 366):
        raise DataValidationError("day_of_year must be in 1..366")
    dt = date(int(year), 1, 1) + timedelta(days=int(day_of_year) - 1)
    return dt.isoformat()


def check_freeze_by_extension(best_by_iso: str, freeze_days: int = 90) -> str:
    """Extend a Best-By date by freeze_days for frozen-at-store products."""
    _req(best_by_iso, "best_by_iso")
    if freeze_days < 0:
        raise DataValidationError("freeze_days cannot be negative")
    dt = date.fromisoformat(str(best_by_iso)) + timedelta(days=int(freeze_days))
    return dt.isoformat()


def flag_unreadable_inkjet_dates(stamp: str) -> bool:
    """Return True if an inkjet date stamp is smudged or unreadable."""
    if not isinstance(stamp, str) or not stamp.strip():
        return True
    return "?" in stamp or "SMUDGE" in stamp.upper()


def calculate_shelf_life_backdate_lot(best_by_iso: str, shelf_life_days: int = 180) -> str:
    """Back-calculate production date from Best-By date and shelf_life_days."""
    _req(best_by_iso, "best_by_iso")
    if shelf_life_days <= 0:
        raise DataValidationError("shelf_life_days must be positive")
    dt = date.fromisoformat(str(best_by_iso)) - timedelta(days=int(shelf_life_days))
    return dt.isoformat()


def match_pack_date_to_best_by(pack_iso: str, best_by_iso: str, expected_days: int = 180) -> bool:
    """Return True if best_by_iso - pack_iso equals expected_days."""
    d1 = date.fromisoformat(str(pack_iso))
    d2 = date.fromisoformat(str(best_by_iso))
    return (d2 - d1).days == int(expected_days)


def handle_month_year_only_stamps(year: int, month: int) -> tuple[str, str]:
    """Expand a YYYY-MM stamp to (first_day_iso, last_day_iso) of that month."""
    if not (1 <= month <= 12):
        raise DataValidationError("month must be in 1..12")
    last_day = calendar.monthrange(int(year), int(month))[1]
    return (date(int(year), int(month), 1).isoformat(), date(int(year), int(month), last_day).isoformat())


def validate_window_chronology(start_iso: str, end_iso: str) -> bool:
    """Verify start_iso <= end_iso."""
    _req(start_iso, "start_iso")
    _req(end_iso, "end_iso")
    if str(end_iso) < str(start_iso):
        raise DataValidationError("end_iso precedes start_iso")
    return True
