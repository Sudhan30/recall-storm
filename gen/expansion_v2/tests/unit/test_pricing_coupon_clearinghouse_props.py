"""Property tests for recallstorm.pricing.coupon_clearinghouse."""
import random
from recallstorm.pricing.coupon_clearinghouse import reconcile_pre_recall_coupon_submissions


def test_coupon_reconciliation_non_negative_props():
    rng = random.Random(42)
    for _ in range(25):
        n = rng.randint(0, 200)
        v = rng.uniform(0.25, 5.00)
        assert reconcile_pre_recall_coupon_submissions(n, v) >= 0.0
