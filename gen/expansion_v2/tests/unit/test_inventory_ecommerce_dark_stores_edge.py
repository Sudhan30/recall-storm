"""Edge case tests for recallstorm.inventory.ecommerce_dark_stores."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.inventory.ecommerce_dark_stores import (
    intercept_staged_curbside_totes,
    sync_virtual_inventory_availability,
)


def test_ecommerce_dark_stores_edge():
    with pytest.raises(DataValidationError):
        intercept_staged_curbside_totes("WM1", [])
    with pytest.raises(DataValidationError):
        sync_virtual_inventory_availability("S1", -1)
