"""Property tests for recallstorm.comms.union_safety_notices."""
import random
from recallstorm.comms.union_safety_notices import provide_ergonomic_heavy_lifting_guide


def test_team_lift_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        w = rng.uniform(5.0, 90.0)
        assert provide_ergonomic_heavy_lifting_guide(w)["team_lift_required"] == (w > 50.0)
