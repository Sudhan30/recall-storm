"""Edge case tests for recallstorm.inventory.cross_dock_allocation."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.inventory.cross_dock_allocation import (
    balance_multi_store_master_cartons,
    recalculation_store_allocation_shorts,
)


def test_cross_dock_allocation_edge():
    with pytest.raises(DataValidationError):
        recalculation_store_allocation_shorts(5, 10)
    with pytest.raises(DataValidationError):
        balance_multi_store_master_cartons(10, 0)
