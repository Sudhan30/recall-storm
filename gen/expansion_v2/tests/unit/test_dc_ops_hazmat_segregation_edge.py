"""Edge case tests for recallstorm.dc_ops.hazmat_segregation."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.dc_ops.hazmat_segregation import (
    coordinate_clean_harbors_lab_pack_pickup,
    generate_epa_hazardous_waste_manifest,
)


def test_hazmat_segregation_edge():
    with pytest.raises(DataValidationError):
        generate_epa_hazardous_waste_manifest("EPA1", [])
    with pytest.raises(DataValidationError):
        coordinate_clean_harbors_lab_pack_pickup("WM1", 0)
