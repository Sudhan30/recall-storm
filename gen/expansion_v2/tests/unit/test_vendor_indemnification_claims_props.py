"""Property tests for recallstorm.vendor.indemnification_claims."""
import random
from recallstorm.vendor.indemnification_claims import verify_vendor_product_liability_coi_limits


def test_coi_limits_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        cov = rng.uniform(1.0, 15.0)
        assert verify_vendor_product_liability_coi_limits(cov, 5.0)["sufficient"] == (cov >= 5.0)
