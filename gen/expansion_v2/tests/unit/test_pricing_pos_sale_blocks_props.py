"""Property tests for recallstorm.pricing.pos_sale_blocks."""
import random
from recallstorm.pricing.pos_sale_blocks import verify_lane_sync_heartbeat_status


def test_lane_sync_percentage_bounds():
    rng = random.Random(42)
    for _ in range(25):
        tot = rng.randint(1, 40)
        syn = rng.randint(0, tot)
        res = verify_lane_sync_heartbeat_status(syn, tot)
        assert 0.0 <= res["pct"] <= 100.0
