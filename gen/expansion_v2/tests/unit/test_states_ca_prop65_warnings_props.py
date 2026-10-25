"""Property tests for recallstorm.states.ca_prop65_warnings."""
import random
from recallstorm.states.ca_prop65_warnings import calculate_prop65_daily_madl_ug


def test_prop65_madl_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        ug = rng.uniform(0.0, 2.0)
        assert calculate_prop65_daily_madl_ug(ug, 0.5)["exceeds_madl"] == (ug > 0.5)
