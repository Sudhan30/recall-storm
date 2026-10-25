"""Edge case tests for recallstorm.dc_ops.automation_inhibits."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.dc_ops.automation_inhibits import (
    isolate_faulted_broken_case_in_shuttle_aisle,
    lock_autostore_or_symbotic_storage_bins,
)


def test_automation_inhibits_edge():
    with pytest.raises(DataValidationError):
        lock_autostore_or_symbotic_storage_bins("CELL1", [])
    with pytest.raises(DataValidationError):
        isolate_faulted_broken_case_in_shuttle_aisle("A1", 0)
