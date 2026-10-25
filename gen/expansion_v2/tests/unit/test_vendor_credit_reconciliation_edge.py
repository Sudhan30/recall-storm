"""Edge case tests for recallstorm.vendor.credit_reconciliation."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.vendor.credit_reconciliation import (
    calculate_cash_discount_reversal_impact,
    match_vendor_credit_memo_to_rma_id,
)


def test_credit_reconciliation_edge():
    with pytest.raises(DataValidationError):
        match_vendor_credit_memo_to_rma_id("CM1", "RMA1", -10.0, 5.0)
    with pytest.raises(DataValidationError):
        calculate_cash_discount_reversal_impact(100.0, 1.5)
