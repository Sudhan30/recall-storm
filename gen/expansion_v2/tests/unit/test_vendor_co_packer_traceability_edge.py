"""Edge case tests for recallstorm.vendor.co_packer_traceability."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.vendor.co_packer_traceability import (
    decode_julian_plant_suffix_on_packaging,
    verify_co_packer_sub_ingredient_suppliers,
)


def test_co_packer_traceability_edge():
    with pytest.raises(DataValidationError):
        decode_julian_plant_suffix_on_packaging("A")
    with pytest.raises(DataValidationError):
        verify_co_packer_sub_ingredient_suppliers("PLT1", [])
