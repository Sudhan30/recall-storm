"""Edge case tests for recallstorm.analytics.financial_impact."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.analytics.financial_impact import (
    compute_net_unrecovered_recall_p_and_l_hit,
    sum_direct_product_write_off_at_cost,
)


def test_financial_impact_edge():
    assert compute_net_unrecovered_recall_p_and_l_hit(1000.0, 1500.0, 0.0) == 0.0
    with pytest.raises(DataValidationError):
        sum_direct_product_write_off_at_cost([-10.0])
