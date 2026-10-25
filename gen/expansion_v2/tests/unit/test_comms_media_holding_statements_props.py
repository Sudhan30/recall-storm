"""Property tests for recallstorm.comms.media_holding_statements."""
import random
from recallstorm.comms.media_holding_statements import flag_viral_tiktok_product_complaints


def test_viral_views_threshold_props():
    rng = random.Random(42)
    for _ in range(25):
        v = rng.randint(0, 25000)
        assert flag_viral_tiktok_product_complaints("V1", v)["viral_alert"] == (v >= 10000)
