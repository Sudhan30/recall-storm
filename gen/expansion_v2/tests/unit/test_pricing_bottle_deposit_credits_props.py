"""Property tests for recallstorm.pricing.bottle_deposit_credits."""
import random
from recallstorm.pricing.bottle_deposit_credits import reconcile_distributor_deposit_chargebacks


def test_distributor_deposit_chargeback_props():
    rng = random.Random(42)
    for _ in range(25):
        cases = rng.randint(1, 50)
        assert reconcile_distributor_deposit_chargebacks(cases, 24, 0.05) == round(cases * 1.2, 2)
