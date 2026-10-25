"""Edge case tests for recallstorm.plan.handoffs."""
from recallstorm.plan.handoffs import build_handoffs, handoff_summary


def test_plan_handoffs_edge():
    res = build_handoffs([], [], [], ["2026-12-31T01:00:00-08:00", "2026-12-31T02:00:00-08:00"])
    assert res == []
    assert sum(handoff_summary([]).values()) == 0
