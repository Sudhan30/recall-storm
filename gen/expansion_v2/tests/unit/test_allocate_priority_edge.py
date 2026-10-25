"""Edge case tests for recallstorm.allocate.priority."""
from recallstorm.allocate.priority import deadline_weight, rank_stores


def test_allocate_priority_edge():
    assert rank_stores([]) == []
    assert deadline_weight(0.0) == 100.0
