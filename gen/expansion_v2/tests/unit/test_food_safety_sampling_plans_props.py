"""Property tests for recallstorm.food_safety.sampling_plans."""
from recallstorm.food_safety.sampling_plans import calculate_icmsf_case_class_plan


def test_severe_icmsf_cases_have_zero_tolerance():
    for c in range(10, 16):
        plan = calculate_icmsf_case_class_plan(c)
        assert plan["c"] == 0
