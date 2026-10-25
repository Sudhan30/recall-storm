"""Property tests for recallstorm.sim.walking."""
import random
from contract import Location
from recallstorm.sim.walking import walk_seconds


def test_walk_seconds_symmetry_props():
    rng = random.Random(42)
    for _ in range(25):
        l1 = Location(f"A{rng.randint(1, 10):02d}", rng.randint(1, 8), 1, 1)
        l2 = Location(f"A{rng.randint(1, 10):02d}", rng.randint(1, 8), 1, 1)
        assert walk_seconds(l1, l2) == walk_seconds(l2, l1)
