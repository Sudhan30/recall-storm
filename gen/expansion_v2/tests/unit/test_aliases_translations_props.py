"""Property tests for recallstorm.aliases.translations."""
from recallstorm.aliases.translations import accent_fold, multilingual_patterns, translated_match


def test_translations_length_preservation():
    for term in multilingual_patterns("RED3"):
        assert len(accent_fold(term)) == len(term)
        sample = f"SUGAR, {term}, SALT"
        m = translated_match(sample, "RED3")
        assert m is not None
        assert sample[m[1] : m[2]] == m[0]
