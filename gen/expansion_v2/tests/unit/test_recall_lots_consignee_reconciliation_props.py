"""Property tests for recallstorm.recall_lots.consignee_reconciliation."""
import random
from recallstorm.recall_lots.consignee_reconciliation import calculate_net_shipped_exposure


def test_net_shipped_exposure_non_negative():
    rng = random.Random(42)
    for _ in range(25):
        s = rng.randint(0, 100)
        r = rng.randint(0, 150)
        assert calculate_net_shipped_exposure(s, r) >= 0
