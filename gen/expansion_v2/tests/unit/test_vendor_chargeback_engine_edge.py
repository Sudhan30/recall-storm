"""Edge case tests for recallstorm.vendor.chargeback_engine."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.vendor.chargeback_engine import (
    calculate_per_store_execution_labor_fee,
    compute_lost_gross_margin_recovery,
)


def test_chargeback_engine_edge():
    with pytest.raises(DataValidationError):
        calculate_per_store_execution_labor_fee(-1, 75.0)
    with pytest.raises(DataValidationError):
        compute_lost_gross_margin_recovery(10, 2.0, 5.0)
