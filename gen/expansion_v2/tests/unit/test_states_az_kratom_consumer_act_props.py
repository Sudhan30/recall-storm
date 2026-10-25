"""Property tests for recallstorm.states.az_kratom_consumer_act."""
import random
from recallstorm.states.az_kratom_consumer_act import verify_az_7_oh_fraction_limit


def test_az_7_oh_limit_props():
    rng = random.Random(42)
    for _ in range(25):
        pct = rng.uniform(0.0, 5.0)
        assert verify_az_7_oh_fraction_limit(pct, 2.0)["compliant"] == (pct <= 2.0)
