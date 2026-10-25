"""Edge case tests for recallstorm.recall_lots.effectiveness_checks."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.recall_lots.effectiveness_checks import (
    calculate_effectiveness_completion_pct,
    select_fda_level_a_through_e_sample,
)


def test_effectiveness_checks_edge():
    with pytest.raises(DataValidationError):
        select_fda_level_a_through_e_sample("Z", ["WM1"])
    with pytest.raises(DataValidationError):
        calculate_effectiveness_completion_pct(10, 5)
