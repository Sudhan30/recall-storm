"""Unit tests for recallstorm.plan.deadline."""
from datetime import datetime
from recallstorm.plan.deadline import (
    DeadlineGuard,
    deadline_for_plan,
    deadline_report,
    deadline_slack_minutes,
    deadline_violations,
    enforce_deadline,
    late_risk,
    shrink_window,
    window_before_deadline,
)


def test_deadline_enforcement():
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    dg = DeadlineGuard(dl)
    assert dg.deadline == dl
    assert deadline_for_plan(dl).startswith("2027-01-01T00:00:00")

    good_w = ["2026-12-30T22:00:00-08:00", "2026-12-31T06:00:00-08:00"]
    bad_w = ["2026-12-31T23:00:00-08:00", "2027-01-01T01:00:00-08:00"]
    assert window_before_deadline(good_w, dl) is True
    assert window_before_deadline(bad_w, dl) is False
    assert deadline_slack_minutes(good_w, dl) > 100
    assert late_risk(good_w, dl) == 0.0
    assert late_risk(bad_w, dl) == 1.0

    s, e = shrink_window(datetime.fromisoformat(bad_w[0]), datetime.fromisoformat(bad_w[1]), dl)
    assert e < dl

    fixed = enforce_deadline([{"type": "shelf_task", "window": bad_w}], dl)
    assert deadline_violations(fixed, dl) == []
    assert deadline_report(fixed, dl)["compliant"] is True
