"""Edge case tests for recallstorm.inventory.reverse_logistics_acct."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.inventory.reverse_logistics_acct import (
    age_unsettled_return_receivables,
    reconcile_crushed_bale_weights,
)


def test_reverse_logistics_acct_edge():
    assert age_unsettled_return_receivables(120) == "OVER_90"
    with pytest.raises(DataValidationError):
        reconcile_crushed_bale_weights(0.0, 100.0)
