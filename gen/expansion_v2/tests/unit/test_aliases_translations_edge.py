"""Edge case tests for recallstorm.aliases.translations."""
import pytest
from recallstorm.aliases.translations import add_translation, translate_alias, translated_match


def test_translations_edge():
    with pytest.raises(ValueError):
        translate_alias("")
    with pytest.raises(ValueError):
        add_translation("RED3", "en", "")
    assert translated_match("", "RED3") is None
    assert translate_alias("UnknownTermXYZ", "en") == "UnknownTermXYZ"
