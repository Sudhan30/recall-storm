"""Property tests for recallstorm.store.backroom."""
import random
from recallstorm.store.backroom import backroom_capacity_left


def test_backroom_capacity_non_negative():
    rng = random.Random(42)
    for _ in range(30):
        cur = rng.randint(0, 1000)
        assert backroom_capacity_left(cur, 500) >= 0
