"""Unit tests for recallstorm.labor.compliance."""
from datetime import datetime
from contract import Associate
from recallstorm.labor.compliance import (
    LaborRules,
    break_required,
    check_labor_rules,
    labor_report,
    labor_violations,
    max_shift_minutes,
    meal_break_window,
    overtime_minutes,
    violation_to_record,
)


def test_labor_compliance():
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    a = Associate("WM1-A01", "WM1", "D01", False, t0, t1)
    assert max_shift_minutes(False) == 480.0
    assert max_shift_minutes(True) == 450.0
    assert break_required(480.0) is True
    mb = meal_break_window(a)
    assert mb is not None
    assert overtime_minutes(500.0, 480.0) == 20.0
    assert check_labor_rules(a, 200.0) == []
    assert len(check_labor_rules(a, 600.0)) == 1
    viols = labor_violations([a], {"WM1-A01": 600.0})
    assert len(viols) == 1
    assert violation_to_record(viols[0])["src"] == "recallstorm/labor/compliance.py"
    assert labor_report([a], {"WM1-A01": 200.0})["violation_count"] == 0
    assert LaborRules().max_shift_mins == 480.0
