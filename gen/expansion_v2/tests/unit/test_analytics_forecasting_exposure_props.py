"""Property tests for recallstorm.analytics.forecasting_exposure."""
import random
from recallstorm.analytics.forecasting_exposure import bound_confidence_interval_on_untracked_lots


def test_confidence_interval_brackets_point_estimate():
    rng = random.Random(42)
    for _ in range(25):
        est = rng.uniform(10.0, 1000.0)
        lo, hi = bound_confidence_interval_on_untracked_lots(est, 0.2)
        assert lo <= est <= hi
