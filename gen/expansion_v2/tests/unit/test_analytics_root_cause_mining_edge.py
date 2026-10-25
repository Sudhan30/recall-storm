"""Edge case tests for recallstorm.analytics.root_cause_mining."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.analytics.root_cause_mining import (
    attribute_misses_to_planogram_unmapped_locs,
    identify_pos_sync_failures_by_isp_carrier,
)


def test_root_cause_mining_edge():
    with pytest.raises(DataValidationError):
        attribute_misses_to_planogram_unmapped_locs(10, 5)
    with pytest.raises(DataValidationError):
        identify_pos_sync_failures_by_isp_carrier({})
