"""Parse roster data into Associates and shift schedules."""
from __future__ import annotations

from datetime import datetime, timedelta

from contract import Associate
from recallstorm.core.clock import minutes_between
from recallstorm.core.errors import DataValidationError
from recallstorm.core.validate import validate_associate


def parse_shift(start_str: str, end_str: str) -> tuple[datetime, datetime]:
    """Parse ISO shift start and end timestamps and verify start < end."""
    try:
        s = datetime.fromisoformat(start_str)
        e = datetime.fromisoformat(end_str)
    except Exception as exc:
        raise DataValidationError(f"Invalid shift timestamps: {start_str!r}, {end_str!r}") from exc
    if e <= s:
        raise DataValidationError("shift_end must be after shift_start")
    return (s, e)


def parse_roster_row(row: dict) -> Associate:
    """Parse a dictionary row into a contract Associate."""
    if not isinstance(row, dict) or not row.get("associate_id"):
        raise DataValidationError("Roster row requires associate_id")
    s, e = parse_shift(str(row["shift_start"]), str(row["shift_end"]))
    is_fl = bool(row.get("is_floater", False))
    st_id = None if is_fl and not row.get("store_id") else str(row.get("store_id", "")).strip() or None
    return Associate(
        associate_id=str(row["associate_id"]).strip(),
        store_id=st_id,
        district=str(row.get("district", "D01")).strip(),
        is_floater=is_fl,
        shift_start=s,
        shift_end=e,
    )


def roster_to_associates(rows: list[dict]) -> list[Associate]:
    """Convert a list of roster dicts into Associate objects."""
    return [parse_roster_row(r) for r in rows]


def shift_minutes(assoc: Associate) -> float:
    """Return total duration of an associate's shift in minutes."""
    return minutes_between(assoc.shift_start, assoc.shift_end)


def floater_pool(associates: list[Associate], district: str | None = None) -> list[Associate]:
    """Return all floater associates, optionally filtered by district."""
    return [a for a in associates if a.is_floater and (district is None or a.district == district)]


def overnight_shift_window(date_str: str, tz_Offset: str = "-08:00") -> tuple[datetime, datetime]:
    """Construct a standard 22:00 to 06:00+1d overnight shift window."""
    start = datetime.fromisoformat(f"{date_str}T22:00:00{tz_Offset}")
    end = start + timedelta(hours=8)
    return (start, end)


def roster_by_store(associates: list[Associate]) -> dict[str, list[Associate]]:
    """Group non-floater associates by store_id."""
    out: dict[str, list[Associate]] = {}
    for a in associates:
        if a.store_id:
            out.setdefault(a.store_id, []).append(a)
    return out


def roster_by_district(associates: list[Associate]) -> dict[str, list[Associate]]:
    """Group associates by district."""
    out: dict[str, list[Associate]] = {}
    for a in associates:
        out.setdefault(a.district, []).append(a)
    return out


def validate_roster(associates: list[Associate]) -> list[str]:
    """Validate a list of Associate objects."""
    issues: list[str] = []
    for a in associates:
        issues.extend(validate_associate(a))
    return issues
