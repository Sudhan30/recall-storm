"""Edge case tests for recallstorm.governance.board_reporting."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.governance.board_reporting import (
    benchmark_compliance_maturity_against_peers,
    compile_quarterly_enterprise_recall_summary,
)


def test_board_reporting_edge():
    with pytest.raises(DataValidationError):
        compile_quarterly_enterprise_recall_summary("2026-Q4", -1, 90.0)
    with pytest.raises(DataValidationError):
        benchmark_compliance_maturity_against_peers(120.0, 85.0)
