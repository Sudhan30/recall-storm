"""Property tests for recallstorm.aliases.spans."""
import random
from recallstorm.aliases.spans import span_from_match, span_text


def test_span_slice_invariance():
    rng = random.Random(42)
    text = "SUGAR, CORN SYRUP, FD&C RED #3, FD&C RED #40, SALT, WATER"
    for _ in range(30):
        a = rng.randint(0, len(text) - 2)
        b = rng.randint(a + 1, len(text))
        sp = span_from_match(text, a, b)
        assert span_text(text, sp) == sp.text
        assert sp.end - sp.start == len(sp.text)
