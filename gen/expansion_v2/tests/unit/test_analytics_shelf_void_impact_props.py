"""Property tests for recallstorm.analytics.shelf_void_impact."""
import random
from recallstorm.analytics.shelf_void_impact import quantify_category_switching_walk_away_rate


def test_walk_away_rate_in_unit_interval():
    rng = random.Random(42)
    for _ in range(25):
        base = rng.randint(10, 200)
        gained = rng.randint(0, 250)
        rate = quantify_category_switching_walk_away_rate(base, gained)
        assert 0.0 <= rate <= 1.0
