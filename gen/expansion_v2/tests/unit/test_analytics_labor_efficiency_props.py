"""Property tests for recallstorm.analytics.labor_efficiency."""
import random
from recallstorm.analytics.labor_efficiency import calibrate_task_time_standards_by_category


def test_calibrated_standard_convex_combination_props():
    rng = random.Random(42)
    for _ in range(25):
        obs = rng.uniform(1.0, 30.0)
        std = rng.uniform(1.0, 30.0)
        cal = calibrate_task_time_standards_by_category(obs, std)
        assert min(obs, std) - 0.01 <= cal <= max(obs, std) + 0.01
