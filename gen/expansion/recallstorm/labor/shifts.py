"""Associate shift windows, deadline clamping, and store/district availability."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from contract import Associate
from recallstorm.core.clock import minutes_between, window_overlaps


@dataclass(frozen=True)
class ShiftCalendar:
    """Roster shift calendar."""

    associates: tuple[Associate, ...]


def shift_window(assoc: Associate) -> tuple[datetime, datetime]:
    """Return (shift_start, shift_end) for an Associate."""
    if not isinstance(assoc, Associate):
        raise TypeError("assoc must be an Associate")
    return assoc.shift_start, assoc.shift_end


def shift_minutes_left(assoc: Associate, used_mins: float = 0.0) -> float:
    """Return remaining shift minutes for an Associate."""
    total = minutes_between(assoc.shift_start, assoc.shift_end)
    return max(0.0, total - max(0.0, used_mins))


def shift_utilization(assoc: Associate, used_mins: float) -> float:
    """Return fraction of shift used in [0.0, 1.0]."""
    total = minutes_between(assoc.shift_start, assoc.shift_end)
    if total <= 0:
        return 0.0
    return round(min(1.0, max(0.0, used_mins) / total), 4)


def shift_overlaps(a1: Associate, a2: Associate) -> bool:
    """Return True if two associates' shifts overlap in time."""
    return window_overlaps((a1.shift_start, a1.shift_end), (a2.shift_start, a2.shift_end))


def clamp_to_shift(assoc: Associate, deadline: datetime) -> tuple[datetime, datetime]:
    """Clamp an associate's shift window so that it ends strictly before deadline."""
    if not isinstance(assoc, Associate):
        raise TypeError("assoc must be an Associate")
    safe_end = deadline - timedelta(minutes=1)
    end = min(assoc.shift_end, safe_end)
    start = min(assoc.shift_start, end - timedelta(minutes=15))
    return start, end


def associates_for_store(associates: list[Associate], store_id: str) -> list[Associate]:
    """Return non-floater associates assigned to store_id, sorted by associate_id."""
    return sorted(
        [a for a in associates if a.store_id == store_id and not a.is_floater],
        key=lambda a: a.associate_id,
    )


def floaters_for_district(associates: list[Associate], district: str) -> list[Associate]:
    """Return floater associates assigned to district, sorted by associate_id."""
    return sorted(
        [a for a in associates if a.is_floater and a.district == district],
        key=lambda a: a.associate_id,
    )


def available_associates(
    associates: list[Associate],
    store_id: str,
    district: str,
    deadline: datetime | None = None,
) -> list[Associate]:
    """Return store associates followed by district floaters available before deadline."""
    local = associates_for_store(associates, store_id)
    flts = floaters_for_district(associates, district)
    combined = local + flts
    if deadline is not None:
        combined = [a for a in combined if a.shift_start < deadline]
    return combined
