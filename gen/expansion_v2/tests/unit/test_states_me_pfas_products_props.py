"""Property tests for recallstorm.states.me_pfas_products."""
import random
from recallstorm.states.me_pfas_products import calculate_me_reporting_fee_tier


def test_me_fee_tier_linear_props():
    rng = random.Random(42)
    for _ in range(25):
        n = rng.randint(1, 40)
        assert calculate_me_reporting_fee_tier(n, 250.0) == n * 250.0
