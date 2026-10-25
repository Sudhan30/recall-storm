"""Associate shift windows, availability, and utilization."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from contract import Associate
from recallstorm.core.clock import clamp_window, minutes_between, window_overlaps


@dataclass
class ShiftCalendar:
    """Collection of associate shifts."""

    associates: list[Associate] = field(default_factory=list)


def shift_window(assoc: Associate, deadline: datetime | None = None) -> tuple[datetime, datetime]:
    """Return the associate's usable shift window, clamped strictly before deadline if provided."""
    end = assoc.shift_end
    if deadline is not None:
        safe_end = deadline - timedelta(minutes=1)
        if safe_end < end:
            end = max(assoc.shift_start + timedelta(minutes=1), safe_end)
    return (assoc.shift_start, end)


def shift_minutes_left(assoc: Associate, used_mins: float = 0.0, deadline: datetime | None = None) -> float:
    """Return remaining shift minutes before shift_end (and deadline)."""
    s, e = shift_window(assoc, deadline=deadline)
    total = max(0.0, minutes_between(s, e))
    return max(0.0, total - float(used_mins))


def associates_for_store(associates: list[Associate], store_id: str) -> list[Associate]:
    """Return non-floater associates assigned to store_id sorted by associate_id."""
    return sorted([a for a in associates if a.store_id == store_id and not a.is_floater], key=lambda x: x.associate_id)


def floaters_for_district(associates: list[Associate], district: str) -> list[Associate]:
    """Return floater associates in district sorted by associate_id."""
    return sorted([a for a in associates if a.is_floater and a.district == district], key=lambda x: x.associate_id)


def available_associates(
    associates: list[Associate], store_id: str, district: str | None = None
) -> list[Associate]:
    """Return store associates plus district floaters available for store_id."""
    direct = associates_for_store(associates, store_id)
    if district:
        return direct + floaters_for_district(associates, district)
    return direct


def shift_overlaps(a1: Associate, a2: Associate) -> bool:
    """Return True if two associates' shifts overlap in time."""
    return window_overlaps((a1.shift_start, a1.shift_end), (a2.shift_start, a2.shift_end))


def clamp_to_shift(window: tuple[datetime, datetime], assoc: Associate) -> tuple[datetime, datetime]:
    """Clamp a task window to lie within assoc's shift_start and shift_end."""
    clamped = clamp_window(window, (assoc.shift_start, assoc.shift_end))
    if clamped is not None:
        return clamped
    return (assoc.shift_start, min(assoc.shift_end, assoc.shift_start + timedelta(minutes=5)))


def shift_utilization(assoc: Associate, worked_mins: float) -> float:
    """Return fraction of shift worked in [0.0, 1.0]."""
    total = minutes_between(assoc.shift_start, assoc.shift_end)
    if total <= 0:
        return 0.0
    return round(min(1.0, max(0.0, worked_mins / total)), 4)
