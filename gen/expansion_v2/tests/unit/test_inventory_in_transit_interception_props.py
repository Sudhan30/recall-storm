"""Property tests for recallstorm.inventory.in_transit_interception."""
import random
from recallstorm.inventory.in_transit_interception import reconcile_short_ship_from_intercept


def test_short_ship_conservation_props():
    rng = random.Random(42)
    for _ in range(25):
        ord_c = rng.randint(10, 100)
        int_c = rng.randint(0, ord_c)
        assert reconcile_short_ship_from_intercept(ord_c, int_c) + int_c == ord_c
