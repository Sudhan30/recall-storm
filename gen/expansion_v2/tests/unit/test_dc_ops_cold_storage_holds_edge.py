"""Edge case tests for recallstorm.dc_ops.cold_storage_holds."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.dc_ops.cold_storage_holds import (
    monitor_ammonia_leak_exposure_in_cold_room,
    schedule_defrost_window_for_held_coils,
)


def test_cold_storage_holds_edge():
    with pytest.raises(DataValidationError):
        monitor_ammonia_leak_exposure_in_cold_room(-5.0)
    with pytest.raises(DataValidationError):
        schedule_defrost_window_for_held_coils("RM1", 25)
