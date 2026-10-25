"""Edge case tests for recallstorm.pricing.wic_ebt_blocks."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.pricing.wic_ebt_blocks import (
    audit_wic_reimbursement_adjustments,
    validate_cereal_size_ounce_substitute,
)


def test_wic_ebt_blocks_edge():
    with pytest.raises(DataValidationError):
        validate_cereal_size_ounce_substitute(0.0, 36.0)
    with pytest.raises(DataValidationError):
        audit_wic_reimbursement_adjustments("CLM1", -5.0)
