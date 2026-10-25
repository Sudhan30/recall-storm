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


def test_plan_deadline():
    dl = deadline_for_plan("2027-01-01T00:00:00-08:00")
    w_ok = ["2026-12-30T22:00:00-08:00", "2026-12-31T02:00:00-08:00"]
    w_late = ["2026-12-31T23:00:00-08:00", "2027-01-01T01:00:00-08:00"]
    assert window_before_deadline(w_ok, dl) is True
    assert window_before_deadline(w_late, dl) is False

    s, e = shrink_window((datetime.fromisoformat(w_late[0]), datetime.fromisoformat(w_late[1])), dl)
    assert e < dl
    assert deadline_slack_minutes((s, e), dl) == 1.0
    assert late_risk((s, e), dl) > 0.9

    recs = [{"type": "shelf_task", "task_id": "T1", "window": w_late}]
    assert len(deadline_violations(recs, dl)) == 1
    fixed = enforce_deadline(recs, dl)
    assert deadline_violations(fixed, dl) == []
    assert deadline_report(fixed, dl)["violation_count"] == 0
    assert DeadlineGuard(dl).deadline == dl
