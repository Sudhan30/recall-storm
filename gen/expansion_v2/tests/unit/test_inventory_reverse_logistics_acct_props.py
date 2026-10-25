"""Property tests for recallstorm.inventory.reverse_logistics_acct."""
import random
from recallstorm.inventory.reverse_logistics_acct import value_return_center_staging_stock


def test_staging_stock_value_props():
    rng = random.Random(42)
    for _ in range(25):
        c = rng.randint(0, 100)
        cost = rng.uniform(5.0, 50.0)
        assert value_return_center_staging_stock(c, cost) >= 0.0
