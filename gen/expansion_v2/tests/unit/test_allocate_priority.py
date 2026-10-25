"""Unit tests for recallstorm.allocate.priority."""
from contract import Store, StoreFormat
from recallstorm.allocate.priority import (
    PriorityModel,
    deadline_weight,
    distance_weight,
    format_weight,
    priority_report,
    priority_score,
    rank_stores,
    store_priority,
    tie_break_key,
)


def test_allocate_priority():
    s1 = Store("WM2000", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    s2 = Store("WM1000", StoreFormat.DISCOUNT, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    assert tie_break_key("WM1000") == "WM1000"
    assert format_weight(StoreFormat.SUPERCENTER) > format_weight(StoreFormat.DISCOUNT)
    assert 0.0 <= distance_weight(34.0, -118.0) <= 1.0
    assert deadline_weight(10.0) == 10.0
    assert store_priority(s1) == 40.0
    assert priority_score(s1, 5) == 45.0
    assert [s.store_id for s in rank_stores([s1, s2])] == ["WM1000", "WM2000"]
    assert priority_report([s1, s2])["store_count"] == 2
    assert PriorityModel().format_factor == 10.0
