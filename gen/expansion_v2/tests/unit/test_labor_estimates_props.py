"""Property tests for recallstorm.labor.estimates."""
import random
from recallstorm.labor.estimates import pull_minutes


def test_pull_minutes_monotonic():
    rng = random.Random(42)
    for _ in range(30):
        u1 = rng.randint(0, 50)
        u2 = u1 + rng.randint(1, 50)
        assert pull_minutes(u2) > pull_minutes(u1)
