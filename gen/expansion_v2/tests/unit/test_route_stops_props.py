"""Property tests for recallstorm.route.stops."""
import random
from contract import Stop
from recallstorm.route.stops import merge_stops


def test_merge_stops_conserves_cases_cube_weight():
    rng = random.Random(42)
    stops = [Stop(f"WM{rng.randint(1, 5)}", rng.randint(1, 10), 2.5, 15.0) for _ in range(25)]
    merged = merge_stops(stops)
    assert sum(s.cases for s in merged) == sum(s.cases for s in stops)
    assert abs(sum(s.cube_ft3 for s in merged) - sum(s.cube_ft3 for s in stops)) < 1e-4
