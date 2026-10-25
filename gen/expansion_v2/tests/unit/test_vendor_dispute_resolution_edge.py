"""Edge case tests for recallstorm.vendor.dispute_resolution."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.vendor.dispute_resolution import (
    apply_partial_settlement_credit_adjustment,
    ingest_vendor_dispute_portal_submission,
)


def test_dispute_resolution_edge():
    with pytest.raises(DataValidationError):
        ingest_vendor_dispute_portal_submission("D1", "V1", 0.0)
    with pytest.raises(DataValidationError):
        apply_partial_settlement_credit_adjustment(100.0, 200.0)
