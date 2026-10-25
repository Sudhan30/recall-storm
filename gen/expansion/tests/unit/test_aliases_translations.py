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


def test_translations_and_folding():
    assert "RED3" in TRANSLATIONS
    assert accent_fold("érythrosine") == "erythrosine"
    assert detect_language("Azucar, Agua, Eritrosina") == "es"
    assert detect_language("Sucre, Farine, Colorant") == "fr"
    assert detect_language("Sugar, Water") == "en"
    assert "eritrosina" in alias_in_language("RED3", "es")
    assert translate_alias("erythrosine", "es") == "eritrosina"
    assert len(multilingual_patterns("RED3")) >= 8
    m = translated_match("INGREDIENTES: AZUCAR, ERITROSINA, AGUA.", "RED3")
    assert m is not None and m[0] == "ERITROSINA"
    rep = language_report(["Sugar", "Azucar, Harina"])
    assert rep["en"] == 1 and rep["es"] == 1
    add_translation("RED3", "es", "rojo eritrosina")
    assert "rojo eritrosina" in alias_in_language("RED3", "es")
