"""Edge case tests for recallstorm.comms.customer_notifications."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.comms.customer_notifications import (
    track_email_bounce_and_open_metrics,
    trigger_automated_robocall_for_class_i,
)


def test_customer_notifications_edge():
    with pytest.raises(DataValidationError):
        trigger_automated_robocall_for_class_i([], "R1")
    with pytest.raises(DataValidationError):
        track_email_bounce_and_open_metrics(10, 20, 5)
