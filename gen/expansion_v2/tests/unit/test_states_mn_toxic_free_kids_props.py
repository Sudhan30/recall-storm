"""Property tests for recallstorm.states.mn_toxic_free_kids."""
import random
from recallstorm.states.mn_toxic_free_kids import check_mn_toy_jewelry_ppm


def test_mn_lead_cadmium_joint_bounds():
    rng = random.Random(42)
    for _ in range(25):
        pb = rng.uniform(0.0, 150.0)
        cd = rng.uniform(0.0, 150.0)
        assert check_mn_toy_jewelry_ppm(pb, cd)["prohibited"] == (pb > 90.0 or cd > 75.0)
