"""Property tests for recallstorm.allocate.demand."""
import random
from recallstorm.allocate.demand import demand_cases


def test_demand_cases_covers_all_units():
    rng = random.Random(42)
    for _ in range(30):
        u = rng.randint(1, 200)
        cu = rng.randint(4, 36)
        c = demand_cases(u, cu)
        assert c * cu >= u
        assert (c - 1) * cu < u
