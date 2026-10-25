"""Edge case tests for recallstorm.pricing.register_prompts."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.pricing.register_prompts import (
    A_B_test_prompt_clarity_speed,
    track_prompt_bypass_rate_by_cashier,
)


def test_register_prompts_edge():
    with pytest.raises(DataValidationError):
        track_prompt_bypass_rate_by_cashier(15, 10)
    with pytest.raises(DataValidationError):
        A_B_test_prompt_clarity_speed(0.0, 5.0)
