"""Edge case tests for recallstorm.pricing.substitute_pricing."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.pricing.substitute_pricing import (
    authorize_equal_or_lesser_sub_price,
    prevent_price_gouging_on_alternatives,
)


def test_substitute_pricing_edge():
    assert prevent_price_gouging_on_alternatives(20.0, 30.0, 0.10)["compliant"] is False
    with pytest.raises(DataValidationError):
        authorize_equal_or_lesser_sub_price(0.0, 3.0)
