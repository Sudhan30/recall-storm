"""Edge case tests for recallstorm.recall_lots.consignee_reconciliation."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.recall_lots.consignee_reconciliation import (
    calculate_net_shipped_exposure,
    reconcile_billed_vs_received_cases,
)


def test_consignee_reconciliation_edge():
    with pytest.raises(DataValidationError):
        reconcile_billed_vs_received_cases(-1, 5)
    with pytest.raises(DataValidationError):
        calculate_net_shipped_exposure(10, -5)
