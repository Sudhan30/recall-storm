"""Edge case tests for recallstorm.food_safety.sanitation_logs."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.food_safety.sanitation_logs import (
    log_food_contact_atp_rlu_scores,
    schedule_listeria_zone_1_swabs,
)


def test_sanitation_logs_edge():
    with pytest.raises(DataValidationError):
        schedule_listeria_zone_1_swabs("WM1", [])
    with pytest.raises(DataValidationError):
        log_food_contact_atp_rlu_scores("S1", -10)
