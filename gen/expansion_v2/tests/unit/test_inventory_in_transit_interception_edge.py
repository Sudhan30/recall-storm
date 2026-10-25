"""Edge case tests for recallstorm.inventory.in_transit_interception."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.inventory.in_transit_interception import reconcile_short_ship_from_intercept


def test_in_transit_interception_edge():
    with pytest.raises(DataValidationError):
        reconcile_short_ship_from_intercept(5, 10)
