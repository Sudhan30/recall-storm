"""Property tests for recallstorm.pricing.wic_ebt_blocks."""
import random
from recallstorm.pricing.wic_ebt_blocks import validate_cereal_size_ounce_substitute


def test_wic_ounce_cap_props():
    rng = random.Random(42)
    for _ in range(25):
        oz = rng.uniform(8.0, 48.0)
        assert validate_cereal_size_ounce_substitute(oz, 36.0)["eligible"] == (oz <= 36.0)
