"""Property tests for recallstorm.rules.preemption."""
from datetime import datetime, timedelta
import random
from contract import Rule
from recallstorm.rules.preemption import stricter_rule


def test_stricter_rule_commutativity():
    rng = random.Random(42)
    base = datetime(2027, 1, 1)
    for i in range(25):
        r1 = Rule(f"RA_{i}", "RED3", ("Red 3",), ("CA",), ("food",), base + timedelta(days=rng.randint(0, 30)), "c", "t")
        r2 = Rule(f"RB_{i}", "RED3", ("Red 3",), ("US",), ("food",), base + timedelta(days=rng.randint(0, 30)), "c", "t")
        assert stricter_rule(r1, r2) == stricter_rule(r2, r1)
