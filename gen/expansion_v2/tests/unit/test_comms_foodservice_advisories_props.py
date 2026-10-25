"""Property tests for recallstorm.comms.foodservice_advisories."""
import random
from recallstorm.comms.foodservice_advisories import log_discarded_prepared_batch_weights


def test_discarded_batch_weights_props():
    rng = random.Random(42)
    for _ in range(25):
        w = round(rng.uniform(0.5, 100.0), 2)
        assert log_discarded_prepared_batch_weights("WM1", w)["weight_lb"] == w
