"""Property tests for recallstorm.food_safety.foreign_material."""
import random
from recallstorm.food_safety.foreign_material import check_fda_hard_sharp_7mm_rule


def test_fda_7mm_rule_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        mm = rng.uniform(0.0, 20.0)
        assert check_fda_hard_sharp_7mm_rule(mm, False)["adulterated"] == (mm >= 7.0)
