"""Property tests for recallstorm.labor.floaters."""
from datetime import datetime, timedelta
from contract import Associate
from recallstorm.labor.floaters import dispatch_floater, one_store_per_window


def test_sequential_floater_dispatches_never_overlap():
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    flt = Associate("FLT-1", None, "D01", True, t0, t1)
    dispatches = []
    cur = t0
    for i in range(5):
        d = dispatch_floater(flt, f"WM{i}", cur, 40.0)
        dispatches.append(d)
        cur = cur + timedelta(minutes=60)
    assert one_store_per_window(dispatches) is True
