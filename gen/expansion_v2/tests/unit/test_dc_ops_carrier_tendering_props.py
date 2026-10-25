"""Property tests for recallstorm.dc_ops.carrier_tendering."""
import random
from recallstorm.dc_ops.carrier_tendering import negotiate_spot_market_backhaul_rates


def test_spot_rate_linear_props():
    rng = random.Random(42)
    for _ in range(25):
        m = rng.randint(10, 500)
        assert negotiate_spot_market_backhaul_rates(float(m), 3.0) == round(m * 3.0, 2)
