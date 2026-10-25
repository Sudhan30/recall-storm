"""Edge case tests for recallstorm.inventory.lot_level_perpetual."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.inventory.lot_level_perpetual import (
    bound_lot_presence_probability,
    export_store_lot_exposure_range,
)


def test_lot_level_perpetual_edge():
    assert bound_lot_presence_probability(0, 0) == 0.0
    with pytest.raises(DataValidationError):
        export_store_lot_exposure_range(10, 5)
