"""Property tests for recallstorm.gs1.lots."""
import random
from recallstorm.gs1.lots import lot_in_range


def test_lot_in_range_monotonic_props():
    rng = random.Random(42)
    for _ in range(30):
        a = rng.randint(1000, 5000)
        b = rng.randint(a, 9000)
        mid = rng.randint(a, b)
        assert lot_in_range(f"LOT{mid}", f"LOT{a}", f"LOT{b}") is True
        assert lot_in_range(f"LOT{b + 1}", f"LOT{a}", f"LOT{b}") is False
