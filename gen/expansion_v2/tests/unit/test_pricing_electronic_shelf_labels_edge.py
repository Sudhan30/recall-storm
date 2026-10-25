"""Edge case tests for recallstorm.pricing.electronic_shelf_labels."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.pricing.electronic_shelf_labels import (
    audit_esl_update_latency_sla,
    flash_esl_led_for_associate_pull,
)


def test_electronic_shelf_labels_edge():
    with pytest.raises(DataValidationError):
        flash_esl_led_for_associate_pull("M1", "RED", 0)
    with pytest.raises(DataValidationError):
        audit_esl_update_latency_sla(-5.0)
