"""Edge case tests for recallstorm.states.ut_cotinine_nicotine."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.ut_cotinine_nicotine import audit_ut_age_scanner_logs, check_ut_nicotine_volume_cap


def test_ut_cotinine_nicotine_edge():
    with pytest.raises(DataValidationError):
        check_ut_nicotine_volume_cap(-1.0)
    with pytest.raises(DataValidationError):
        audit_ut_age_scanner_logs("WM1", 120.0)
