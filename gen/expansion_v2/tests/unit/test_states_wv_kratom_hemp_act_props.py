"""Property tests for recallstorm.states.wv_kratom_hemp_act."""
import random
from recallstorm.states.wv_kratom_hemp_act import check_wv_mitragynine_limit


def test_wv_mitragynine_limit_props():
    rng = random.Random(42)
    for _ in range(25):
        pct = rng.uniform(0.0, 5.0)
        assert check_wv_mitragynine_limit(pct, 2.0)["compliant"] == (pct <= 2.0)
