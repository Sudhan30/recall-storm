"""Property tests for recallstorm.food_safety.water_ice_safety."""
import random
from recallstorm.food_safety.water_ice_safety import track_post_advisory_line_flushing


def test_line_flushing_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        mins = rng.uniform(0.0, 30.0)
        assert track_post_advisory_line_flushing("WM1", mins)["sufficient"] == (mins >= 10.0)
