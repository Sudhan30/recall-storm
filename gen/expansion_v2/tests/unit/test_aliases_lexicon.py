"""Unit tests for recallstorm.aliases.lexicon."""
from datetime import datetime
from contract import Rule
from recallstorm.aliases.lexicon import (
    Lexicon,
    add_alias,
    additive_for_alias,
    aliases_for,
    ci_number_for,
    e_number_for,
    lexicon_from_rules,
    load_lexicon,
    translations_for,
)


def test_lexicon_functions():
    lex = load_lexicon()
    assert isinstance(lex, Lexicon)
    assert "E127" in aliases_for("RED3", lex)
    assert additive_for_alias("erythrosine", lex) == "RED3"
    assert e_number_for("RED3") == "E127"
    assert ci_number_for("RED3") == "CI 45430"
    assert len(translations_for("RED3")) >= 5
    add_alias(lex, "RED3", "Custom Red 3")
    assert additive_for_alias("Custom Red 3", lex) == "RED3"
    r = Rule("R1", "RED3", ("SpecialRed3",), ("CA",), ("food",), datetime(2027, 1, 1), "ref", "txt")
    lex2 = lexicon_from_rules([r])
    assert "SpecialRed3" in aliases_for("RED3", lex2)
