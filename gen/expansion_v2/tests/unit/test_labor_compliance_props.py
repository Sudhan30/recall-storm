"""Property tests for recallstorm.labor.compliance."""
from datetime import datetime
import random
from contract import Associate
from recallstorm.labor.compliance import check_labor_rules


def test_under_capacity_never_violates():
    rng = random.Random(42)
    t0 = datetime.fromisoformat("2026-12-30T22:00:00-08:00")
    t1 = datetime.fromisoformat("2026-12-31T06:00:00-08:00")
    a = Associate("A1", "WM1", "D01", False, t0, t1)
    for _ in range(25):
        mins = rng.uniform(0.0, 480.0)
        assert check_labor_rules(a, mins) == []
