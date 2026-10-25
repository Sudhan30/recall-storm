"""Unit tests for recallstorm.labor.shifts."""
from datetime import datetime
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


def test_labor_shifts():
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    a1 = Associate("WM1-A01", "WM1", "D01", False, t0, t1)
    a2 = Associate("FLT-D01", None, "D01", True, t0, t1)

    assert shift_window(a1) == (t0, t1)
    assert shift_minutes_left(a1, 80.0) == 400.0
    assert associates_for_store([a1, a2], "WM1") == [a1]
    assert floaters_for_district([a1, a2], "D01") == [a2]
    assert len(available_associates([a1, a2], "WM1", "D01")) == 2
    assert shift_overlaps(a1, a2) is True
    assert clamp_to_shift((t0, t1), a1) == (t0, t1)
    assert shift_utilization(a1, 240.0) == 0.5
    cal = ShiftCalendar([a1, a2])
    assert len(cal.associates) == 2
