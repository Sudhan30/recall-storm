"""Edge case tests for recallstorm.comms.regulator_reports."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.comms.regulator_reports import (
    compile_fda_district_recall_status_report,
    verify_zero_stock_attestation_accuracy,
)


def test_regulator_reports_edge():
    assert verify_zero_stock_attestation_accuracy(True, 5)["accurate"] is False
    with pytest.raises(DataValidationError):
        compile_fda_district_recall_status_report("R1", 60, 50)
