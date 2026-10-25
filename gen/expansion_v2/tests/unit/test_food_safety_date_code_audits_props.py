"""Property tests for recallstorm.food_safety.date_code_audits."""
import random
from recallstorm.food_safety.date_code_audits import score_department_freshness_index


def test_freshness_index_bounds():
    rng = random.Random(42)
    for _ in range(25):
        total = rng.randint(1, 200)
        exp = rng.randint(0, total)
        idx = score_department_freshness_index(total, exp)
        assert 0.0 <= idx <= 100.0
