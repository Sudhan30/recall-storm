"""Property tests for recallstorm.pricing.promotion_conflicts."""
from recallstorm.pricing.promotion_conflicts import adjust_vendor_coop_ad_funding_claim


def test_coop_ad_funding_bounds():
    for d in range(0, 8):
        val = adjust_vendor_coop_ad_funding_claim(700.0, d, 7)
        assert 0.0 <= val <= 700.0
