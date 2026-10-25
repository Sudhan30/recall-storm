"""Property tests for recallstorm.route.returns."""
import random
from contract import Sku
from recallstorm.route.returns import cases_by_store, returns_to_stops


def test_returns_to_stops_case_conservation():
    rng = random.Random(42)
    skus = {f"S{i}": Sku(f"S{i}", "00012345678905", "N", "B", "c", "I", True, False, 12, 1.5, 8.0) for i in range(5)}
    pulled = {(f"WM{rng.randint(1, 5)}", f"S{rng.randint(0, 4)}"): rng.randint(1, 15) for _ in range(25)}
    stops = returns_to_stops(pulled, skus)
    assert sum(s.cases for s in stops) == sum(cases_by_store(pulled).values())
