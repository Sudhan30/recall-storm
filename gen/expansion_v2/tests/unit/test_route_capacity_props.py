"""Property tests for recallstorm.route.capacity."""
from datetime import datetime
import random
from contract import Stop, Truck
from recallstorm.route.capacity import capacity_check, remaining_cube, remaining_weight


def test_capacity_check_matches_remaining_bounds():
    rng = random.Random(42)
    t = Truck("T1", "DC1", 3400.0, 40000.0, datetime(2026, 12, 31, 8, 0))
    for _ in range(25):
        c = rng.uniform(100.0, 5000.0)
        w = rng.uniform(1000.0, 50000.0)
        s = Stop("WM1", 10, c, w)
        assert capacity_check(t, [s]) == (remaining_cube(t, [s]) >= 0 and remaining_weight(t, [s]) >= 0)
