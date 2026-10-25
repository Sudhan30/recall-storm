"""Edge case tests for recallstorm.analytics.shelf_void_impact."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.analytics.shelf_void_impact import (
    measure_days_of_empty_facing_post_pull,
    score_dc_emergency_allocation_fill_rate,
)


def test_shelf_void_impact_edge():
    with pytest.raises(DataValidationError):
        measure_days_of_empty_facing_post_pull(10, 5)
    with pytest.raises(DataValidationError):
        score_dc_emergency_allocation_fill_rate(120, 100)
