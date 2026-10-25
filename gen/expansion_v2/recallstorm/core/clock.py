"""Timezone conversions, local wall-clock comparisons, and time windows."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from recallstorm.core.errors import DataValidationError


def to_local(dt: datetime, tz_name: str) -> datetime:
    """Convert a timezone-aware or naive datetime to the target IANA timezone."""
    if not isinstance(dt, datetime):
        raise TypeError("dt must be a datetime")
    try:
        tz = ZoneInfo(tz_name)
    except Exception as exc:
        raise DataValidationError(f"Invalid timezone {tz_name!r}") from exc
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


def from_local(naive_dt: datetime, tz_name: str) -> datetime:
    """Attach the given IANA timezone to a wall-clock datetime."""
    if not isinstance(naive_dt, datetime):
        raise TypeError("naive_dt must be a datetime")
    try:
        tz = ZoneInfo(tz_name)
    except Exception as exc:
        raise DataValidationError(f"Invalid timezone {tz_name!r}") from exc
    return naive_dt.replace(tzinfo=None).replace(tzinfo=tz)


def local_wall(dt: datetime, tz_name: str | None = None) -> datetime:
    """Return a naive local wall-clock datetime for comparing with Rule.effective."""
    if not isinstance(dt, datetime):
        raise TypeError("dt must be a datetime")
    if tz_name and dt.tzinfo is not None:
        return dt.astimezone(ZoneInfo(tz_name)).replace(tzinfo=None)
    return dt.replace(tzinfo=None)


def naive_local(dt: datetime, tz_name: str | None = None) -> datetime:
    """Alias for local_wall returning naive local datetime."""
    return local_wall(dt, tz_name=tz_name)


def is_before_deadline(dt: datetime, deadline: datetime, strict: bool = True) -> bool:
    """Check whether dt is before deadline (strictly before when strict=True)."""
    if not isinstance(dt, datetime) or not isinstance(deadline, datetime):
        raise TypeError("dt and deadline must be datetimes")
    if (dt.tzinfo is None) != (deadline.tzinfo is None):
        d1 = dt.replace(tzinfo=None)
        d2 = deadline.replace(tzinfo=None)
    else:
        d1, d2 = dt, deadline
    return d1 < d2 if strict else d1 <= d2


def minutes_between(start: datetime, end: datetime) -> float:
    """Return signed elapsed minutes from start to end."""
    if not isinstance(start, datetime) or not isinstance(end, datetime):
        raise TypeError("start and end must be datetimes")
    if (start.tzinfo is None) != (end.tzinfo is None):
        s, e = start.replace(tzinfo=None), end.replace(tzinfo=None)
    else:
        s, e = start, end
    return (e - s).total_seconds() / 60.0


def window_overlaps(w1: tuple[datetime, datetime], w2: tuple[datetime, datetime]) -> bool:
    """Return True if half-open intervals [w1[0], w1[1]) and [w2[0], w2[1]) overlap."""
    s1, e1 = w1
    s2, e2 = w2
    if e1 <= s1 or e2 <= s2:
        return False
    return max(s1, s2) < min(e1, e2)


def clamp_window(
    w: tuple[datetime, datetime], bounds: tuple[datetime, datetime]
) -> tuple[datetime, datetime] | None:
    """Clamp window w to bounds; return None if the intersection is empty."""
    s = max(w[0], bounds[0])
    e = min(w[1], bounds[1])
    if e <= s:
        return None
    return (s, e)


def iso_with_offset(dt: datetime, tz_name: str | None = None) -> str:
    """Format a datetime as ISO 8601 with UTC offset."""
    if not isinstance(dt, datetime):
        raise TypeError("dt must be a datetime")
    target = dt
    if target.tzinfo is None:
        tz = ZoneInfo(tz_name or "America/Los_Angeles")
        target = target.replace(tzinfo=tz)
    elif tz_name:
        target = target.astimezone(ZoneInfo(tz_name))
    return target.isoformat(timespec="seconds")
