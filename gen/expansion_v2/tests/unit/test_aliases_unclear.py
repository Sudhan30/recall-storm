"""Unit tests for recallstorm.aliases.unclear."""
from recallstorm.aliases.unclear import (
    generic_color_phrases,
    is_generic_color,
    is_unreadable,
    needs_human_review,
    ocr_noise_ratio,
    readability_score,
    redact_noise,
    truncated_label,
    unclear_reason,
)


def test_unclear_detection():
    # Ambiguous color alone -> unclear
    ambig = "SUGAR, CORN SYRUP, CITRIC ACID, ARTIFICIAL COLOR."
    assert is_generic_color(ambig) is True
    assert len(generic_color_phrases(ambig)) == 1
    assert needs_human_review(ambig) is True
    assert unclear_reason(ambig) is not None

    # Artificial colors followed by specific list -> clear!
    specific = "SUGAR, ARTIFICIAL COLORS (RED 40, YELLOW 5, BLUE 1)."
    assert is_generic_color(specific) is False
    assert needs_human_review(specific) is False

    # Unreadable / truncated
    assert is_unreadable("SUGAR, SMUDGED ???") is True
    assert truncated_label("SUGAR, CORN SYRUP, FD&C...") is True
    assert ocr_noise_ratio("A???B") > 0.5
    assert readability_score("SUGAR, WATER, SALT.") == 1.0
    assert redact_noise("A???B") == "A B"
