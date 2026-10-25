"""Edge case tests for recallstorm.states.me_pfas_products."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.me_pfas_products import calculate_me_reporting_fee_tier, check_me_intentionally_added_pfas


def test_me_pfas_products_edge():
    assert check_me_intentionally_added_pfas("PFAS-FREE CERAMIC")["has_pfas"] is False
    with pytest.raises(DataValidationError):
        calculate_me_reporting_fee_tier(-1)
