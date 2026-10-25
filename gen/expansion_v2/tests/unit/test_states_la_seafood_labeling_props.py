"""Property tests for recallstorm.states.la_seafood_labeling."""
import random
from recallstorm.states.la_seafood_labeling import verify_la_placard_font_size


def test_la_font_size_props():
    rng = random.Random(42)
    for _ in range(25):
        pt = rng.randint(10, 60)
        assert verify_la_placard_font_size(pt, 30)["compliant"] == (pt >= 30)
