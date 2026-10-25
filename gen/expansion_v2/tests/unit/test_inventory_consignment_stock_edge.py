"""Edge case tests for recallstorm.inventory.consignment_stock."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.inventory.consignment_stock import exclude_consignment_from_shrink_gl


def test_consignment_stock_edge():
    with pytest.raises(DataValidationError):
        exclude_consignment_from_shrink_gl(100.0, 200.0)
