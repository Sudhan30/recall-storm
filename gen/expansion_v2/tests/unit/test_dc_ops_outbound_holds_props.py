"""Property tests for recallstorm.dc_ops.outbound_holds."""
import random
from recallstorm.dc_ops.outbound_holds import re_cube_shorted_store_delivery_trailer


def test_re_cube_conservation_props():
    rng = random.Random(42)
    for _ in range(25):
        orig = round(rng.uniform(500.0, 3400.0), 2)
        rem = round(rng.uniform(0.0, orig), 2)
        assert abs((re_cube_shorted_store_delivery_trailer(orig, rem) + rem) - orig) <= 0.02
