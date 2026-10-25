"""Edge case tests for recallstorm.comms.pharmacy_alerts."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.comms.pharmacy_alerts import (
    process_central_fill_intercept_requests,
    quarantine_will_call_waiting_bin_bags,
)


def test_pharmacy_alerts_edge():
    with pytest.raises(DataValidationError):
        quarantine_will_call_waiting_bin_bags("WM1", [])
    with pytest.raises(DataValidationError):
        process_central_fill_intercept_requests("CF1", [])
