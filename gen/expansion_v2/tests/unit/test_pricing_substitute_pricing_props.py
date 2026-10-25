"""Property tests for recallstorm.pricing.substitute_pricing."""
import random
from recallstorm.pricing.substitute_pricing import authorize_equal_or_lesser_sub_price


def test_sub_price_never_exceeds_recalled_price():
    rng = random.Random(42)
    for _ in range(25):
        p1 = round(rng.uniform(1.0, 20.0), 2)
        p2 = round(rng.uniform(1.0, 20.0), 2)
        assert authorize_equal_or_lesser_sub_price(p1, p2) <= p1
        assert authorize_equal_or_lesser_sub_price(p1, p2) <= p2
