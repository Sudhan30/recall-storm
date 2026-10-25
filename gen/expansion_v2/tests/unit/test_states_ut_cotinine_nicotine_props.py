"""Property tests for recallstorm.states.ut_cotinine_nicotine."""
import random
from recallstorm.states.ut_cotinine_nicotine import check_ut_nicotine_volume_cap


def test_ut_nicotine_cap_props():
    rng = random.Random(42)
    for _ in range(25):
        mg = rng.uniform(0.0, 60.0)
        assert check_ut_nicotine_volume_cap(mg, 36.0)["compliant"] == (mg <= 36.0)
