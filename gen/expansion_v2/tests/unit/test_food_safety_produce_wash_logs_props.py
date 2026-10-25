"""Property tests for recallstorm.food_safety.produce_wash_logs."""
import random
from recallstorm.food_safety.produce_wash_logs import verify_peracetic_acid_ppm_range


def test_paa_ppm_range_props():
    rng = random.Random(42)
    for _ in range(25):
        ppm = rng.uniform(10.0, 120.0)
        assert verify_peracetic_acid_ppm_range(ppm, 40.0, 80.0)["compliant"] == (40.0 <= ppm <= 80.0)
