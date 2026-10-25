"""Edge case tests for recallstorm.vendor.reformulation_tracker."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.vendor.reformulation_tracker import report_category_compliance_readiness_pct


def test_reformulation_tracker_edge():
    with pytest.raises(DataValidationError):
        report_category_compliance_readiness_pct(25, 20)
