"""Edge case tests for recallstorm.comms.foodservice_advisories."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.comms.foodservice_advisories import (
    log_discarded_prepared_batch_weights,
    notify_corporate_catering_event_clients,
)


def test_foodservice_advisories_edge():
    with pytest.raises(DataValidationError):
        notify_corporate_catering_event_clients([])
    with pytest.raises(DataValidationError):
        log_discarded_prepared_batch_weights("WM1", -5.0)
