"""Edge case tests for recallstorm.food_safety.pest_control_holds."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.food_safety.pest_control_holds import (
    map_adjacent_pallet_buffer_zone,
    quarantine_compromised_dry_goods,
)


def test_pest_control_holds_edge():
    assert map_adjacent_pallet_buffer_zone(1, 2) == [1, 2, 3]
    with pytest.raises(DataValidationError):
        quarantine_compromised_dry_goods("WM1", [])
