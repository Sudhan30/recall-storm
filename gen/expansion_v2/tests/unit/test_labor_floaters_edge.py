"""Edge case tests for recallstorm.labor.floaters."""
from datetime import datetime
from contract import Associate
from recallstorm.labor.floaters import dispatch_floater, one_store_per_window, validate_floaters


def test_labor_floaters_overlap_detection():
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    flt = Associate("FLT-1", None, "D01", True, t0, t1)
    d1 = dispatch_floater(flt, "WM1", t0, 60.0)
    d2 = dispatch_floater(flt, "WM2", t0, 60.0)  # Same time, different store!
    assert one_store_per_window([d1, d2]) is False
    assert len(validate_floaters([d1, d2])) == 1
