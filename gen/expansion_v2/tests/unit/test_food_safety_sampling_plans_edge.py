"""Edge case tests for recallstorm.food_safety.sampling_plans."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.food_safety.sampling_plans import (
    calculate_icmsf_case_class_plan,
    evaluate_wgs_snp_distance_match,
)


def test_sampling_plans_edge():
    with pytest.raises(DataValidationError):
        calculate_icmsf_case_class_plan(99)
    with pytest.raises(DataValidationError):
        evaluate_wgs_snp_distance_match(-1)
