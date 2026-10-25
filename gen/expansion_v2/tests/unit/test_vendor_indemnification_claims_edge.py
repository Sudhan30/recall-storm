"""Edge case tests for recallstorm.vendor.indemnification_claims."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.vendor.indemnification_claims import (
    coordinate_outside_counsel_litigation_hold,
    verify_vendor_product_liability_coi_limits,
)


def test_indemnification_claims_edge():
    with pytest.raises(DataValidationError):
        verify_vendor_product_liability_coi_limits(-1.0)
    with pytest.raises(DataValidationError):
        coordinate_outside_counsel_litigation_hold("R1", [])
