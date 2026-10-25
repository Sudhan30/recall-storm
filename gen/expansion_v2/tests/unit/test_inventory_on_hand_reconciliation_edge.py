"""Edge case tests for recallstorm.inventory.on_hand_reconciliation."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.inventory.on_hand_reconciliation import (
    calculate_unexplained_lot_discrepancy,
    compare_physical_pull_to_on_hand,
)


def test_on_hand_reconciliation_edge():
    with pytest.raises(DataValidationError):
        compare_physical_pull_to_on_hand(-1, 10)
    with pytest.raises(DataValidationError):
        calculate_unexplained_lot_discrepancy(10, -1, 5)
