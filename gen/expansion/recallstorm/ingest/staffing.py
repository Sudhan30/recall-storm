"""Associate roster and overnight shift window parser."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from contract import Associate
from recallstorm.core.clock import from_local, minutes_between
from recallstorm.core.errors import DataValidationError
from recallstorm.core.validate import validate_associate


def parse_shift(start_str: str, end_str: str, tz_name: str = "America/Los_Angeles") -> tuple[datetime, datetime]:
    """Parse shift start and end ISO strings, attaching tz_name if naive."""
    try:
        s = datetime.fromisoformat(start_str)
        e = datetime.fromisoformat(end_str)
    except ValueError as exc:
        raise DataValidationError(f"Invalid shift datetime: {start_str} / {end_str}") from exc
    if s.tzinfo is None:
        s = from_local(s, tz_name)
    if e.tzinfo is None:
        e = from_local(e, tz_name)
    if e <= s:
        raise DataValidationError("shift_end must be after shift_start")
    return s, e


def parse_roster_row(row: dict) -> dict:
    """Validate and normalize a staffing roster row dictionary."""
    if not isinstance(row, dict) or not row.get("associate_id"):
        raise DataValidationError("Roster row requires associate_id")
    is_floater = bool(row.get("is_floater", False))
    store_id = str(row["store_id"]).strip() if row.get("store_id") else None
    if not is_floater and not store_id:
        raise DataValidationError("Non-floater associate requires store_id")
    s, e = parse_shift(
        str(row.get("shift_start", "2026-12-30T22:00:00-08:00")),
        str(row.get("shift_end", "2026-12-31T06:00:00-08:00")),
        str(row.get("tz", "America/Los_Angeles")),
    )
    return {
        "associate_id": str(row["associate_id"]).strip(),
        "store_id": store_id,
        "district": str(row.get("district", "D01")).strip(),
        "is_floater": is_floater,
        "shift_start": s,
        "shift_end": e,
    }


def roster_to_associates(rows: list[dict]) -> list[Associate]:
    """Convert a list of roster dicts into Associate dataclasses."""
    return [Associate(**parse_roster_row(r)) for r in rows]


def shift_minutes(assoc: Associate) -> float:
    """Return total duration of an associate's shift in minutes."""
    if not isinstance(assoc, Associate):
        raise TypeError("assoc must be an Associate")
    return minutes_between(assoc.shift_start, assoc.shift_end)


def floater_pool(associates: list[Associate], district: str | None = None) -> list[Associate]:
    """Return all floater associates, optionally filtered by district."""
    return [
        a for a in associates if a.is_floater and (district is None or a.district == district)
    ]


def overnight_shift_window(day: date | str, tz_name: str = "America/Los_Angeles") -> tuple[datetime, datetime]:
    """Build standard overnight stocking window (22:00 to 06:00 next day) in local timezone."""
    d = date.fromisoformat(day) if isinstance(day, str) else day
    start_naive = datetime(d.year, d.month, d.day, 22, 0, 0)
    end_naive = start_naive + timedelta(hours=8)
    return from_local(start_naive, tz_name), from_local(end_naive, tz_name)


def roster_by_store(associates: list[Associate]) -> dict[str, list[Associate]]:
    """Group non-floater associates by store_id."""
    out: dict[str, list[Associate]] = {}
    for a in associates:
        if a.store_id:
            out.setdefault(a.store_id, []).append(a)
    return out


def roster_by_district(associates: list[Associate]) -> dict[str, list[Associate]]:
    """Group all associates by district."""
    out: dict[str, list[Associate]] = {}
    for a in associates:
        out.setdefault(a.district, []).append(a)
    return out


def validate_roster(associates: list[Associate]) -> list[str]:
    """Validate a list of Associate instances."""
    issues: list[str] = []
    for a in associates:
        issues.extend(validate_associate(a))
    return issues
