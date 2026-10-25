"""Property tests for recallstorm.aliases.detect."""
from recallstorm.aliases.detect import find_first_match
from recallstorm.aliases.lexicon import aliases_for


def test_detect_exact_span_invariance():
    for alias in aliases_for("RED3"):
        text = f"INGREDIENTS: SUGAR, CORN SYRUP, {alias}, CITRIC ACID, SALT."
        m = find_first_match(text, ("Red 3", "E127"), "RED3")
        assert m is not None
        assert text[m.start : m.end] == m.match_text
