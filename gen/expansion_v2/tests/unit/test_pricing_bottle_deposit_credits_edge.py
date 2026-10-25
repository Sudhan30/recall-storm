"""Edge case tests for recallstorm.pricing.bottle_deposit_credits."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.pricing.bottle_deposit_credits import (
    calculate_unredeemed_crv_tax_credit,
    handle_multi_state_deposit_rate_diffs,
)


def test_bottle_deposit_credits_edge():
    assert handle_multi_state_deposit_rate_diffs("TX", 12.0) == 0.0
    with pytest.raises(DataValidationError):
        calculate_unredeemed_crv_tax_credit(-10)
