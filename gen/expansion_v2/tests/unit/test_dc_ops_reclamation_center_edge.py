"""Edge case tests for recallstorm.dc_ops.reclamation_center."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.dc_ops.reclamation_center import (
    calculate_reclamation_processing_cost_per_unit,
    route_scanned_returns_to_vendor_gaylords,
)


def test_reclamation_center_edge():
    with pytest.raises(DataValidationError):
        route_scanned_returns_to_vendor_gaylords("V1", 0)
    with pytest.raises(DataValidationError):
        calculate_reclamation_processing_cost_per_unit(100.0, 0)
