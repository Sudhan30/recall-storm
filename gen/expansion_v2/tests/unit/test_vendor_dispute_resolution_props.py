"""Property tests for recallstorm.vendor.dispute_resolution."""
import random
from recallstorm.vendor.dispute_resolution import apply_partial_settlement_credit_adjustment


def test_partial_settlement_conservation_props():
    rng = random.Random(42)
    for _ in range(25):
        orig = round(rng.uniform(100.0, 10000.0), 2)
        cred = round(rng.uniform(0.0, orig), 2)
        net = apply_partial_settlement_credit_adjustment(orig, cred)
        assert abs((net + cred) - orig) <= 0.02
