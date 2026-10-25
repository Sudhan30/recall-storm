"""Edge case tests for recallstorm.pricing.coupon_clearinghouse."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.pricing.coupon_clearinghouse import (
    reconcile_pre_recall_coupon_submissions,
    void_clipped_loyalty_wallet_offers,
)


def test_coupon_clearinghouse_edge():
    with pytest.raises(DataValidationError):
        void_clipped_loyalty_wallet_offers("OFF1", -1)
    with pytest.raises(DataValidationError):
        reconcile_pre_recall_coupon_submissions(-5, 1.0)
