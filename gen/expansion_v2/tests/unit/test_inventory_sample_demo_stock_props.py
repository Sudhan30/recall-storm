"""Property tests for recallstorm.inventory.sample_demo_stock."""
import random
from recallstorm.inventory.sample_demo_stock import reconcile_expensed_demo_unit_transfers


def test_reconcile_demo_transfers_additive():
    rng = random.Random(42)
    for _ in range(25):
        a = rng.randint(0, 50)
        b = rng.randint(0, 20)
        assert reconcile_expensed_demo_unit_transfers(a, b) == a + b
