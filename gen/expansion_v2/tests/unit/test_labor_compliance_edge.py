"""Edge case tests for recallstorm.labor.compliance."""
from datetime import datetime
from contract import Associate
from recallstorm.labor.compliance import break_required, meal_break_window, overtime_minutes


def test_labor_compliance_edge():
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T01:00:00-08:00")
    short_assoc = Associate("A1", "WM1", "D01", False, t0, t1)
    assert break_required(180.0) is False
    assert meal_break_window(short_assoc) is None
    assert overtime_minutes(100.0) == 0.0
