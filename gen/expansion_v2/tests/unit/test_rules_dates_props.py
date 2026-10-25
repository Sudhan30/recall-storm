"""Property tests for recallstorm.rules.dates."""
from datetime import datetime, timedelta
import random
from contract import Rule
from recallstorm.rules.dates import is_prohibited_at, sell_through_allowed


def test_prohibited_and_sell_through_partition():
    rng = random.Random(42)
    eff = datetime(2027, 1, 1, 0, 0, 0)
    r = Rule("R1", "RED3", ("Red 3",), ("CA",), ("food",), eff, "c", "t")
    for _ in range(30):
        delta_sec = rng.randint(-100000, 100000)
        t = eff + timedelta(seconds=delta_sec)
        assert is_prohibited_at(r, t) != sell_through_allowed(r, t)
        assert is_prohibited_at(r, t) == (delta_sec >= 0)
