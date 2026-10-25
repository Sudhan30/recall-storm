"""Property tests for recallstorm.inventory.cross_dock_allocation."""
import random
from recallstorm.inventory.cross_dock_allocation import recalculation_store_allocation_shorts


def test_recalculation_shorts_non_negative_props():
    rng = random.Random(42)
    for _ in range(25):
        p = rng.randint(5, 100)
        c = rng.randint(0, p)
        assert recalculation_store_allocation_shorts(p, c) == p - c
