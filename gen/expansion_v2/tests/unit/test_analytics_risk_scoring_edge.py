"""Edge case tests for recallstorm.analytics.risk_scoring."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.analytics.risk_scoring import (
    calculate_demographic_vulnerable_pop_index,
    score_store_by_historical_audit_failures,
)


def test_risk_scoring_edge():
    with pytest.raises(DataValidationError):
        score_store_by_historical_audit_failures(15, 10)
    with pytest.raises(DataValidationError):
        calculate_demographic_vulnerable_pop_index(60.0, 60.0)
