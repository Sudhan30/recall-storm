"""Edge case tests for recallstorm.inventory.quarantine_bins."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.inventory.quarantine_bins import (
    consolidate_partial_hold_cases,
    track_quarantine_bin_capacity_cube,
)


def test_quarantine_bins_edge():
    assert track_quarantine_bin_capacity_cube(250.0, 200.0)["overflow"] is True
    with pytest.raises(DataValidationError):
        consolidate_partial_hold_cases(-5, 12)
