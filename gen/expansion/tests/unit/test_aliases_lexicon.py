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


def test_lexicon_operations():
    lex = load_lexicon()
    assert isinstance(lex, Lexicon)
    assert "E127" in aliases_for("RED3", lex)
    assert additive_for_alias("erythrosine", lex) == "RED3"
    assert e_number_for("RED3") == "E127"
    assert ci_number_for("RED3") == "CI 45430"
    assert "eritrosina" in translations_for("RED3")
    lex2 = add_alias(lex, "RED3", "Custom Red 3")
    assert additive_for_alias("Custom Red 3", lex2) == "RED3"
    r = Rule("R1", "RED3", ("Special Dye 3",), ("CA",), ("food",), datetime(2027, 1, 1), "ref", "src")
    lex3 = lexicon_from_rules([r])
    assert "Special Dye 3" in aliases_for("RED3", lex3)
