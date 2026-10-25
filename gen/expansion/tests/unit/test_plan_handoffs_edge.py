"""Edge tests for recallstorm.plan.handoffs."""
from recallstorm.plan.handoffs import build_handoffs


def test_handoffs_empty():
    assert build_handoffs([], []) == []
