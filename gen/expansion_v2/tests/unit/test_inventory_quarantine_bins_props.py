"""Property tests for recallstorm.inventory.quarantine_bins."""
import random
from recallstorm.inventory.quarantine_bins import consolidate_partial_hold_cases


def test_consolidate_partial_cases_identity():
    rng = random.Random(42)
    for _ in range(25):
        u = rng.randint(0, 500)
        cp = rng.randint(4, 36)
        cases, rem = consolidate_partial_hold_cases(u, cp)
        assert cases * cp + rem == u
