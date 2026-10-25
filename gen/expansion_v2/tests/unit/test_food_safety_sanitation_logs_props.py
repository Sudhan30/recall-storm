"""Property tests for recallstorm.food_safety.sanitation_logs."""
import random
from recallstorm.food_safety.sanitation_logs import verify_quaternary_ammonia_ppm


def test_quat_ppm_window_props():
    rng = random.Random(42)
    for _ in range(25):
        ppm = rng.uniform(50.0, 600.0)
        assert verify_quaternary_ammonia_ppm(ppm, 200.0, 400.0)["in_range"] == (200.0 <= ppm <= 400.0)
