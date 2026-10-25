"""Edge case tests for recallstorm.analytics.trend_reports."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.analytics.trend_reports import (
    analyze_additive_ban_readiness_burn_down,
    chart_allergen_vs_micro_recall_proportions,
)


def test_trend_reports_edge():
    with pytest.raises(DataValidationError):
        analyze_additive_ban_readiness_burn_down([])
    with pytest.raises(DataValidationError):
        chart_allergen_vs_micro_recall_proportions(0, 0, 0)
