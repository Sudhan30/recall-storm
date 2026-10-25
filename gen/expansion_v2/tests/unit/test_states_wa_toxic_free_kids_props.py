"""Property tests for recallstorm.states.wa_toxic_free_kids."""
import random
from recallstorm.states.wa_toxic_free_kids import check_wa_phthalates_ppm


def test_wa_phthalates_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        ppm = rng.uniform(0.0, 2500.0)
        assert check_wa_phthalates_ppm(ppm, 1000.0)["violation"] == (ppm > 1000.0)
