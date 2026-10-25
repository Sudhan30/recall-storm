"""Property tests for recallstorm.food_safety.haccp_deviations."""
import random
from recallstorm.food_safety.haccp_deviations import verify_cooling_curve_compliance


def test_cooling_curve_two_stage_props():
    rng = random.Random(42)
    for _ in range(25):
        t2 = rng.uniform(45.0, 90.0)
        t6 = rng.uniform(33.0, 55.0)
        assert verify_cooling_curve_compliance(t2, t6)["compliant"] == (t2 <= 70.0 and t6 <= 41.0)
