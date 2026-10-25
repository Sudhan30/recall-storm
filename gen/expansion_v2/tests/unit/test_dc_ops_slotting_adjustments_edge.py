"""Edge case tests for recallstorm.dc_ops.slotting_adjustments."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.dc_ops.slotting_adjustments import (
    calculate_cubic_feet_needed_for_recall_hold,
    optimize_forklift_travel_to_compactor_bay,
)


def test_slotting_adjustments_edge():
    with pytest.raises(DataValidationError):
        calculate_cubic_feet_needed_for_recall_hold(-1, 2.0)
    with pytest.raises(DataValidationError):
        optimize_forklift_travel_to_compactor_bay({})
