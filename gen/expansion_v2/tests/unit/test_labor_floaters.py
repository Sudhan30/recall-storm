"""Unit tests for recallstorm.labor.floaters."""
from datetime import datetime
from contract import Associate, Store, StoreFormat
from recallstorm.core.jsonl import validate_record
from recallstorm.labor.floaters import (
    FloaterPool,
    dispatch_floater,
    floater_handoffs,
    floater_need,
    floater_plan_summary,
    floater_travel_minutes,
    floater_windows,
    one_store_per_window,
    validate_floaters,
)


def test_labor_floaters():
    assert floater_need(500.0, 300.0) == 200.0
    s1 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    s2 = Store("WM2", StoreFormat.SUPERCENTER, "CA", "LA", 34.2, -118.2, "D01", "DC1", "America/Los_Angeles")
    assert floater_travel_minutes(s1, s2) >= 10.0

    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    flt = Associate("FLT-1", None, "D01", True, t0, t1)
    d1 = dispatch_floater(flt, "WM1", t0, 60.0)
    d2 = dispatch_floater(flt, "WM2", datetime.fromisoformat("2026-12-31T00:00:00-08:00"), 60.0)
    assert len(floater_windows([d1, d2], "FLT-1")) == 2
    assert one_store_per_window([d1, d2]) is True
    assert validate_floaters([d1, d2]) == []
    hnds = floater_handoffs([d1])
    assert validate_record(hnds[0], "handoff") == []
    assert floater_plan_summary([d1, d2])["valid"] is True
    pool = FloaterPool([flt], [d1])
    assert len(pool.dispatches) == 1
