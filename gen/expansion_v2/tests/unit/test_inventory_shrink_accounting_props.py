"""Property tests for recallstorm.inventory.shrink_accounting."""
import random
from recallstorm.inventory.shrink_accounting import allocate_destruction_hauling_fees


def test_hauling_fee_allocation_sum_props():
    rng = random.Random(42)
    for _ in range(25):
        c1 = rng.randint(1, 50)
        c2 = rng.randint(1, 50)
        res = allocate_destruction_hauling_fees(1000.0, {"WM1": c1, "WM2": c2})
        assert abs((res["WM1"] + res["WM2"]) - 1000.0) <= 0.05
