"""Edge case tests for recallstorm.dc_ops.yard_management."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.dc_ops.yard_management import (
    manage_detention_clock_on_held_equipment,
    monitor_quarantined_reefer_fuel_and_temp,
)


def test_yard_management_edge():
    with pytest.raises(DataValidationError):
        monitor_quarantined_reefer_fuel_and_temp("TR1", 120.0)
    assert manage_detention_clock_on_held_equipment(24.0, 48.0, 15.0) == 0.0
