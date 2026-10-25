"""Property tests for recallstorm.dc_ops.slotting_adjustments."""
import random
from recallstorm.dc_ops.slotting_adjustments import calculate_cubic_feet_needed_for_recall_hold


def test_surge_cube_exceeds_raw_cube():
    rng = random.Random(42)
    for _ in range(25):
        c = rng.randint(1, 100)
        cb = rng.uniform(0.5, 4.0)
        assert calculate_cubic_feet_needed_for_recall_hold(c, cb, 1.25) >= round(c * cb, 2)
