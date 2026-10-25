"""Property tests for recallstorm.analytics.supplier_benchmarking."""
import random
from recallstorm.analytics.supplier_benchmarking import score_vendor_responsiveness_during_drills


def test_responsiveness_score_bounds():
    rng = random.Random(42)
    for _ in range(25):
        mins = rng.uniform(0.0, 120.0)
        assert 0.0 <= score_vendor_responsiveness_during_drills(mins, 30.0) <= 100.0
