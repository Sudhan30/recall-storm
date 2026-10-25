"""Edge case tests for recallstorm.states.il_food_safety_act."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.states.il_food_safety_act import (
    assess_il_distributor_liability,
    calculate_il_sell_through_days,
    track_il_phase_out_schedule,
)


def test_il_food_safety_act_edge():
    assert calculate_il_sell_through_days(-10) == 0
    with pytest.raises(DataValidationError):
        assess_il_distributor_liability(-1)
    with pytest.raises(DataValidationError):
        track_il_phase_out_schedule("M1", 150.0)
