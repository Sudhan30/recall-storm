"""Edge case tests for recallstorm.aliases.unclear."""
from recallstorm.aliases.unclear import is_unreadable, needs_human_review, readability_score


def test_unclear_edge():
    assert is_unreadable("") is True
    assert is_unreadable("  ") is True
    assert readability_score("") == 0.0
    assert needs_human_review("SUGAR, FD&C") is True
