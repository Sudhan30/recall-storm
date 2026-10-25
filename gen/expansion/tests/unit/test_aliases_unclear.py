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


def test_unclear_labels():
    vague = "SUGAR, CORN SYRUP, ARTIFICIAL COLOR, CITRIC ACID."
    assert is_generic_color(vague) is True
    assert generic_color_phrases(vague) == ["ARTIFICIAL COLOR"]
    assert needs_human_review(vague) is True
    assert "Vague color" in (unclear_reason(vague) or "")

    specific = "SUGAR, ARTIFICIAL COLORS (RED 40, YELLOW 5, BLUE 1)."
    assert is_generic_color(specific) is False
    assert needs_human_review(specific) is False

    garbled = "SUGAR, ???@@@###$$$ UNREADABLE"
    assert is_unreadable(garbled) is True
    assert ocr_noise_ratio(garbled) > 0.1
    assert readability_score(garbled) < 0.5
    assert truncated_label("SUGAR, CORN SYRUP...") is True
    assert "@" not in redact_noise(garbled)
