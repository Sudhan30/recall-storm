"""Edge case tests for recallstorm.dc_ops.pallet_license_plates."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.dc_ops.pallet_license_plates import (
    generate_split_pallet_rework_work_order,
    verify_gs1_128_sscc_check_digit_integrity,
)


def test_pallet_license_plates_edge():
    assert verify_gs1_128_sscc_check_digit_integrity("123") is False
    with pytest.raises(DataValidationError):
        generate_split_pallet_rework_work_order("L1", 0)
