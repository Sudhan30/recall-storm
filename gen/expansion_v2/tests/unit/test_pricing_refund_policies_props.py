"""Property tests for recallstorm.pricing.refund_policies."""
import random
from recallstorm.pricing.refund_policies import bypass_return_window_day_limits


def test_return_window_always_accepted_for_recalls():
    rng = random.Random(42)
    for _ in range(25):
        days = rng.randint(0, 1000)
        assert bypass_return_window_day_limits(days)["accepted"] is True
