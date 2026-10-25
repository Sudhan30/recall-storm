"""Edge case tests for recallstorm.inventory.sample_demo_stock."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.inventory.sample_demo_stock import (
    calculate_unbilled_sample_exposure,
    quarantine_demo_prep_cart_inventory,
)


def test_sample_demo_stock_edge():
    with pytest.raises(DataValidationError):
        quarantine_demo_prep_cart_inventory("SAMS1", "CART1", -1)
    with pytest.raises(DataValidationError):
        calculate_unbilled_sample_exposure(-2, 5.0)
