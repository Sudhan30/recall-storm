"""Property tests for recallstorm.analytics.drill_kpis."""
import random
from recallstorm.analytics.drill_kpis import compute_lot_capture_accuracy_precision


def test_precision_in_unit_interval_props():
    rng = random.Random(42)
    for _ in range(25):
        tp = rng.randint(1, 100)
        fp = rng.randint(0, 100)
        p = compute_lot_capture_accuracy_precision(tp, fp)
        assert 0.0 < p <= 1.0
