"""Unit tests for recallstorm.aliases.translations."""
from recallstorm.aliases.translations import (
    TRANSLATIONS,
    accent_fold,
    add_translation,
    alias_in_language,
    detect_language,
    language_report,
    multilingual_patterns,
    translate_alias,
    translated_match,
)


def test_translations():
    assert "RED3" in TRANSLATIONS
    assert accent_fold("érythrosine") == "erythrosine"
    assert detect_language("AZUCAR, AGUA, ROJO 3") == "es"
    assert detect_language("SUCRE, EAU, ROUGE 3") == "fr"
    assert "eritrosina" in alias_in_language("RED3", "es")
    assert translate_alias("eritrosina", "en") == "FD&C Red No. 3"
    assert len(multilingual_patterns("RED3")) >= 10
    m = translated_match("INGREDIENTES: AZUCAR, ERITROSINA, SAL", "RED3")
    assert m is not None and m[0] == "ERITROSINA"
    rep = language_report("AZUCAR, ROJO 3")
    assert rep["language"] == "es" and "RED3" in rep["matches"]
    add_translation("RED3", "it", "eritrosina_it")
    assert "eritrosina_it" in alias_in_language("RED3", "it")
