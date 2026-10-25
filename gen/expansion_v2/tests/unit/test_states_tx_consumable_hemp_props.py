"""Property tests for recallstorm.states.tx_consumable_hemp."""
import random
from recallstorm.states.tx_consumable_hemp import check_tx_delta9_thc_pct


def test_tx_thc_limit_props():
    rng = random.Random(42)
    for _ in range(25):
        pct = rng.uniform(0.0, 1.0)
        assert check_tx_delta9_thc_pct(pct, 0.3)["compliant"] == (pct <= 0.3)
