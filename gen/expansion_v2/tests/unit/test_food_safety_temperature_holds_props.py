"""Property tests for recallstorm.food_safety.temperature_holds."""
import random
from recallstorm.food_safety.temperature_holds import evaluate_fda_tcs_four_hour_rule


def test_tcs_four_hour_rule_props():
    rng = random.Random(42)
    for _ in range(25):
        mins = rng.uniform(0.0, 360.0)
        assert evaluate_fda_tcs_four_hour_rule(mins, 45.0)["discard"] == (mins >= 240.0)
