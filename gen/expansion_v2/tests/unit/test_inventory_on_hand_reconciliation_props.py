"""Property tests for recallstorm.inventory.on_hand_reconciliation."""
import random
from recallstorm.inventory.on_hand_reconciliation import calculate_unexplained_lot_discrepancy


def test_lot_discrepancy_identity_props():
    rng = random.Random(42)
    for _ in range(25):
        sold = rng.randint(0, 50)
        pulled = rng.randint(0, 50)
        shipped = sold + pulled
        assert calculate_unexplained_lot_discrepancy(shipped, sold, pulled) == 0
