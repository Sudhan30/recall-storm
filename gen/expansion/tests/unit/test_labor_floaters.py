"""Unit tests for recallstorm.labor.floaters."""
from datetime import datetime, timezone
from contract import Associate, Store, StoreFormat
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


def test_floaters_operations():
    assert floater_need(500.0, 400.0) == 100.0
    st1 = Store("WM1", StoreFormat.SUPERCENTER, "CA", "LA", 34.0, -118.0, "D01", "DC1", "America/Los_Angeles")
    st2 = Store("WM2", StoreFormat.SUPERCENTER, "CA", "LA", 34.1, -118.1, "D01", "DC1", "America/Los_Angeles")
    assert floater_travel_minutes(st1, st2) >= 10.0

    dt = datetime(2026, 12, 30, 22, 0, tzinfo=timezone.utc)
    flt = Associate("FLT-1", None, "D01", True, dt, dt)
    d1 = dispatch_floater(flt, "WM1", ["2026-12-30T22:00:00-08:00", "2026-12-31T01:00:00-08:00"], ["TSK-1"])
    d2 = dispatch_floater(flt, "WM2", ["2026-12-31T02:00:00-08:00", "2026-12-31T05:00:00-08:00"], ["TSK-2"])
    assert len(floater_windows([d1, d2])["FLT-1"]) == 2
    assert one_store_per_window([d1, d2]) is True
    assert validate_floaters([d1, d2]) == []
    hnds = floater_handoffs([d1, d2])
    assert len(hnds) == 2 and hnds[0]["kind"] == "FLOATER"
    pool = FloaterPool("D01", [flt], [d1, d2])
    assert floater_plan_summary(pool.dispatches)["valid"] is True
