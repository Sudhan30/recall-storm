"""Property tests for recallstorm.vendor.private_label_qa."""
import random
from recallstorm.vendor.private_label_qa import score_copacker_food_safety_culture


def test_copacker_score_bounds():
    rng = random.Random(42)
    for _ in range(25):
        s = rng.uniform(0.0, 100.0)
        res = score_copacker_food_safety_culture(s, rng.choice([True, False]))
        assert 0.0 <= res <= 100.0
