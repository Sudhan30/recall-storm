"""Edge case tests for recallstorm.food_safety.date_code_audits."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.food_safety.date_code_audits import score_department_freshness_index


def test_date_code_audits_edge():
    with pytest.raises(DataValidationError):
        score_department_freshness_index(10, 20)
