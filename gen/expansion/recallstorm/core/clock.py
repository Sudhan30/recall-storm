"""Timezone conversions, wall-clock comparisons, and time window operations."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from recallstorm.core.errors import DataValidationError


def _get_tz(tz_name: str) -> ZoneInfo:
    if not isinstance(tz_name, str) or not tz_name.strip():
        raise DataValidationError("tz_name must be a non-empty string")
    try:
        return ZoneInfo(tz_name.strip())
    except ZoneInfoNotFoundError as exc:
        raise DataValidationError(f"Unknown timezone: {tz_name}") from exc


def to_local(dt: datetime, tz_name: str) -> datetime:
    """Convert a timezone-aware datetime to the target timezone."""
    if not isinstance(dt, datetime):
        raise TypeError("dt must be a datetime")
    tz = _get_tz(tz_name)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


def from_local(naive_dt: datetime, tz_name: str) -> datetime:
    """Attach a local timezone to a naive datetime."""
    if not isinstance(naive_dt, datetime):
        raise TypeError("naive_dt must be a datetime")
    tz = _get_tz(tz_name)
    return naive_dt.replace(tzinfo=tz)


def local_wall(dt: datetime, tz_name: str | None = None) -> datetime:
    """Return naive wall-clock datetime in tz_name (or strip tzinfo if tz_name is None)."""
    if not isinstance(dt, datetime):
        raise TypeError("dt must be a datetime")
    if tz_name:
        tz = _get_tz(tz_name)
        if dt.tzinfo is not None:
            return dt.astimezone(tz).replace(tzinfo=None)
        return dt
    return dt.replace(tzinfo=None)


def naive_local(dt: datetime, tz_name: str | None = None) -> datetime:
    """Alias for local_wall: convert aware datetime to naive local wall-clock."""
    return local_wall(dt, tz_name)


def is_before_deadline(dt: datetime | str, deadline: datetime | str) -> bool:
    """Return True if dt is strictly before deadline (dt < deadline)."""
    d1 = datetime.fromisoformat(dt) if isinstance(dt, str) else dt
    d2 = datetime.fromisoformat(deadline) if isinstance(deadline, str) else deadline
    if not isinstance(d1, datetime) or not isinstance(d2, datetime):
        raise TypeError("dt and deadline must be datetime or ISO strings")
    if (d1.tzinfo is None) != (d2.tzinfo is None):
        d1 = d1.replace(tzinfo=None)
        d2 = d2.replace(tzinfo=None)
    return d1 < d2


def minutes_between(start: datetime | str, end: datetime | str) -> float:
    """Return signed minutes elapsed from start to end."""
    s = datetime.fromisoformat(start) if isinstance(start, str) else start
    e = datetime.fromisoformat(end) if isinstance(end, str) else end
    if not isinstance(s, datetime) or not isinstance(e, datetime):
        raise TypeError("start and end must be datetime or ISO strings")
    return (e - s).total_seconds() / 60.0


def window_overlaps(
    w1: tuple[datetime | str, datetime | str] | list[str],
    w2: tuple[datetime | str, datetime | str] | list[str],
) -> bool:
    """Return True if two half-open intervals [start, end) overlap."""
    if len(w1) != 2 or len(w2) != 2:
        raise ValueError("Windows must have length 2")
    s1 = datetime.fromisoformat(w1[0]) if isinstance(w1[0], str) else w1[0]
    e1 = datetime.fromisoformat(w1[1]) if isinstance(w1[1], str) else w1[1]
    s2 = datetime.fromisoformat(w2[0]) if isinstance(w2[0], str) else w2[0]
    e2 = datetime.fromisoformat(w2[1]) if isinstance(w2[1], str) else w2[1]
    if e1 < s1 or e2 < s2:
        raise ValueError("Window end cannot precede start")
    return max(s1, s2) < min(e1, e2)


def clamp_window(
    window: tuple[datetime, datetime],
    bounds: tuple[datetime, datetime],
) -> tuple[datetime, datetime]:
    """Clamp a (start, end) window to lie within bounds=(min_dt, max_dt)."""
    s, e = window
    b_start, b_end = bounds
    if b_end <= b_start:
        raise ValueError("bounds end must be after bounds start")
    clamped_s = max(s, b_start)
    clamped_e = min(e, b_end)
    if clamped_e <= clamped_s:
        clamped_s = b_start
        clamped_e = b_end
    return clamped_s, clamped_e


def iso_with_offset(dt: datetime, tz_name: str = "America/Los_Angeles") -> str:
    """Format a datetime as ISO 8601 string with explicit UTC offset."""
    if not isinstance(dt, datetime):
        raise TypeError("dt must be a datetime")
    if dt.tzinfo is None:
        dt = from_local(dt, tz_name)
    return dt.isoformat(timespec="seconds")
