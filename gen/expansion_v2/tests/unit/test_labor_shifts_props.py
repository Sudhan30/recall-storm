"""Property tests for recallstorm.labor.shifts."""
from datetime import datetime
import random
from contract import Associate
from recallstorm.labor.shifts import shift_utilization


def test_shift_utilization_bounds():
    rng = random.Random(42)
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    a = Associate("A1", "WM1", "D01", False, t0, t1)
    for _ in range(30):
        u = shift_utilization(a, rng.uniform(-50.0, 1000.0))
        assert 0.0 <= u <= 1.0
