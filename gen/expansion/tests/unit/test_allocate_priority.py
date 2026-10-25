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


def test_priority_functions():
    pm = PriorityModel()
    assert pm.format_factor == 10.0
    st1 = Store("WM2", StoreFormat.DISCOUNT, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    st2 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    assert format_weight(StoreFormat.SUPERCENTER) > format_weight(StoreFormat.DISCOUNT)
    assert distance_weight(34.0, -118.0) > 0
    assert deadline_weight(12.0) == 2.0
    assert store_priority(st2) > store_priority(st1)
    assert priority_score(st2, 5) > store_priority(st2)
    assert tie_break_key(st1) == ("DC1", "WM2")
    assert rank_stores([st1, st2]) == [st2, st1]
    assert priority_report([st1, st2])["ordered_ids"] == ["WM1", "WM2"]
