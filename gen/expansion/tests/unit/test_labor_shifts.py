"""Unit tests for recallstorm.labor.shifts."""
from datetime import datetime, timezone
from contract import Associate
from recallstorm.labor.shifts import (
    ShiftCalendar,
    associates_for_store,
    available_associates,
    clamp_to_shift,
    floaters_for_district,
    shift_minutes_left,
    shift_overlaps,
    shift_utilization,
    shift_window,
)


def test_shifts_functions():
    s = datetime(2026, 12, 30, 22, 0, tzinfo=timezone.utc)
    e = datetime(2026, 12, 31, 6, 0, tzinfo=timezone.utc)
    dl = datetime(2027, 1, 1, 0, 0, tzinfo=timezone.utc)
    a1 = Associate("WM1-A01", "WM1", "D01", False, s, e)
    a2 = Associate("FLT-D01", None, "D01", True, s, e)

    cal = ShiftCalendar((a1, a2))
    assert len(cal.associates) == 2
    assert shift_window(a1) == (s, e)
    assert shift_minutes_left(a1, 180.0) == 300.0
    assert shift_utilization(a1, 240.0) == 0.5
    assert shift_overlaps(a1, a2) is True
    cs, ce = clamp_to_shift(a1, dl)
    assert ce < dl
    assert associates_for_store([a1, a2], "WM1") == [a1]
    assert floaters_for_district([a1, a2], "D01") == [a2]
    assert available_associates([a1, a2], "WM1", "D01", dl) == [a1, a2]
