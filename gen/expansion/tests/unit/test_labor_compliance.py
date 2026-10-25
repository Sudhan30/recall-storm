"""Unit tests for recallstorm.labor.compliance."""
from datetime import datetime, timezone
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
    rules = LaborRules("CA")
    assert rules.max_mins == max_shift_minutes("CA") == 480
    assert break_required(360.0) is True
    s = datetime(2026, 12, 30, 22, 0, tzinfo=timezone.utc)
    e = datetime(2026, 12, 31, 6, 0, tzinfo=timezone.utc)
    bs, be = meal_break_window(s, e)
    assert (be - bs).total_seconds() == 1800
    assert overtime_minutes(500.0) == 20.0

    assoc = Associate("A1", "WM1", "D01", False, s, e)
    assert check_labor_rules(assoc, 200.0) == []
    viols = labor_violations([assoc], {"A1": 500.0})
    assert len(viols) >= 1
    assert violation_to_record(viols[0])["associate_id"] == "A1"
    rep = labor_report([assoc], {"A1": 200.0})
    assert rep["violation_count"] == 0
