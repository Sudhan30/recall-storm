"""Property tests for recallstorm.analytics.trend_reports."""
import random
from recallstorm.analytics.trend_reports import chart_allergen_vs_micro_recall_proportions


def test_recall_proportions_sum_to_one():
    rng = random.Random(42)
    for _ in range(25):
        a = rng.randint(1, 50)
        m = rng.randint(1, 50)
        d = rng.randint(1, 50)
        p = chart_allergen_vs_micro_recall_proportions(a, m, d)
        assert abs((p["allergen"] + p["micro"] + p["additive"]) - 1.0) <= 0.001
