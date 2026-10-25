"""Edge tests for recallstorm.labor.floaters."""
from datetime import datetime, timezone
import pytest
from contract import Associate
from recallstorm.labor.floaters import (
    dispatch_floater,
    one_store_per_window,
    validate_floaters,
)


def test_floaters_edge():
    dt = datetime(2026, 12, 30, 22, 0, tzinfo=timezone.utc)
    non_flt = Associate("A1", "WM1", "D01", False, dt, dt)
    with pytest.raises(ValueError):
        dispatch_floater(non_flt, "WM1", ["2026-12-30T22:00:00-08:00", "2026-12-30T23:00:00-08:00"])

    flt = Associate("FLT-1", None, "D01", True, dt, dt)
    d1 = dispatch_floater(flt, "WM1", ["2026-12-30T22:00:00-08:00", "2026-12-31T02:00:00-08:00"])
    d2 = dispatch_floater(flt, "WM2", ["2026-12-31T01:00:00-08:00", "2026-12-31T03:00:00-08:00"])
    assert one_store_per_window([d1, d2]) is False
    assert validate_floaters([d1, d2]) != []
