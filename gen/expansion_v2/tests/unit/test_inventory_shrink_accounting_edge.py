"""Edge case tests for recallstorm.inventory.shrink_accounting."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.inventory.shrink_accounting import (
    audit_high_value_shrink_approvals,
    calculate_landed_cost_extended_value,
)


def test_shrink_accounting_edge():
    assert audit_high_value_shrink_approvals(75000.0, False)["compliant"] is False
    with pytest.raises(DataValidationError):
        calculate_landed_cost_extended_value(-10, 2.0)
