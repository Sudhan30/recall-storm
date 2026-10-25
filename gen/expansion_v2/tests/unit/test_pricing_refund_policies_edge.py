"""Edge case tests for recallstorm.pricing.refund_policies."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.pricing.refund_policies import (
    enable_no_receipt_full_retail_refund,
    reconcile_recall_refund_tender_totals,
)


def test_refund_policies_edge():
    with pytest.raises(DataValidationError):
        enable_no_receipt_full_retail_refund("S1", 0.0)
    with pytest.raises(DataValidationError):
        reconcile_recall_refund_tender_totals([-5.0])
