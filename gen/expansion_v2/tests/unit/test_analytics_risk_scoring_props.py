"""Property tests for recallstorm.analytics.risk_scoring."""
import random
from recallstorm.analytics.risk_scoring import update_risk_weights_from_post_mortem


def test_missed_pull_always_increases_risk_weight():
    rng = random.Random(42)
    for _ in range(25):
        w = rng.uniform(0.5, 10.0)
        assert update_risk_weights_from_post_mortem(w, True) > update_risk_weights_from_post_mortem(w, False)
