"""Edge tests for recallstorm.aliases.translations."""
import pytest
from recallstorm.aliases.translations import (
    accent_fold,
    add_translation,
    translate_alias,
    translated_match,
)


def test_translations_edge():
    assert translated_match("", "RED3") is None
    assert translate_alias("unknown_term", "es") == "unknown_term"
    with pytest.raises(TypeError):
        accent_fold(123)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        translate_alias("", "es")
    with pytest.raises(ValueError):
        add_translation("", "es", "x")
