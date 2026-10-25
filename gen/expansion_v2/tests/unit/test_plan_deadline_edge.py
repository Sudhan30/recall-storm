"""Edge case tests for recallstorm.plan.deadline."""
from datetime import datetime
from recallstorm.plan.deadline import late_risk, window_before_deadline


def test_plan_deadline_edge():
    dl = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    assert window_before_deadline([], dl) is False
    # Exact deadline is a violation (must end strictly before deadline)
    assert window_before_deadline(["2026-12-31T22:00:00-08:00", "2027-01-01T00:00:00-08:00"], dl) is False
    assert late_risk((dl, dl), dl) == 1.0
