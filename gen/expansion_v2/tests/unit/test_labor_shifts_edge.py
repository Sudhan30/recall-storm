"""Edge case tests for recallstorm.labor.shifts."""
from datetime import datetime
from contract import Associate
from recallstorm.labor.shifts import clamp_to_shift, shift_window


def test_labor_shifts_edge():
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    early_deadline = datetime.fromisoformat("2026-12-31T02:00:00-08:00")
    a = Associate("A1", "WM1", "D01", False, t0, t1)
    _, end = shift_window(a, deadline=early_deadline)
    assert end < early_deadline
    outside = (datetime.fromisoformat("2026-12-30T10:00:00-08:00"), datetime.fromisoformat("2026-12-30T11:00:00-08:00"))
    clamped = clamp_to_shift(outside, a)
    assert clamped[0] >= a.shift_start and clamped[1] <= a.shift_end
