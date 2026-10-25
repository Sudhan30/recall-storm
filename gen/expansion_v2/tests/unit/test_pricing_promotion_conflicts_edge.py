"""Edge case tests for recallstorm.pricing.promotion_conflicts."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.pricing.promotion_conflicts import adjust_vendor_coop_ad_funding_claim


def test_promotion_conflicts_edge():
    with pytest.raises(DataValidationError):
        adjust_vendor_coop_ad_funding_claim(100.0, 10, 7)
