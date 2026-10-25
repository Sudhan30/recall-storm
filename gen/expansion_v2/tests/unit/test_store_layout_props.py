"""Property tests for recallstorm.store.layout."""
import random
from contract import Location
from recallstorm.store.layout import walking_distance


def test_walking_distance_metric_ axioms():
    rng = random.Random(42)
    for _ in range(25):
        l1 = Location(f"A{rng.randint(1, 20):02d}", rng.randint(1, 10), 1, 1)
        l2 = Location(f"A{rng.randint(1, 20):02d}", rng.randint(1, 10), 1, 1)
        l3 = Location(f"A{rng.randint(1, 20):02d}", rng.randint(1, 10), 1, 1)
        assert walking_distance(l1, l1) == 0.0
        assert walking_distance(l1, l2) == walking_distance(l2, l1)
        assert walking_distance(l1, l3) <= walking_distance(l1, l2) + walking_distance(l2, l3) + 1e-6
