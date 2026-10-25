"""Edge case tests for recallstorm.recall_lots.serial_traceability."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.recall_lots.serial_traceability import (
    calculate_serial_recovery_rate,
    match_sscc18_pallet_labels,
)


def test_serial_traceability_edge():
    with pytest.raises(DataValidationError):
        match_sscc18_pallet_labels("12345")
    with pytest.raises(DataValidationError):
        calculate_serial_recovery_rate(15, 10)
