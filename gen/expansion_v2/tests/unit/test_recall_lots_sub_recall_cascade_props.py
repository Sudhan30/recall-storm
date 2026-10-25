"""Property tests for recallstorm.recall_lots.sub_recall_cascade."""
import random
from recallstorm.recall_lots.sub_recall_cascade import calculate_generational_dilution_factor


def test_dilution_factor_in_unit_interval():
    rng = random.Random(42)
    for _ in range(25):
        batch = rng.uniform(10.0, 500.0)
        raw = rng.uniform(0.0, batch)
        f = calculate_generational_dilution_factor(raw, batch)
        assert 0.0 <= f <= 1.0
