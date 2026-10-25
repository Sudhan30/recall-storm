"""Edge case tests for recallstorm.aliases.lexicon."""
import pytest
from recallstorm.aliases.lexicon import add_alias, additive_for_alias, aliases_for, e_number_for, load_lexicon


def test_lexicon_edge():
    lex = load_lexicon()
    assert aliases_for("UNKNOWN_ADDITIVE", lex) == ()
    assert additive_for_alias("", lex) is None
    assert e_number_for("UNKNOWN") is None
    with pytest.raises(ValueError):
        add_alias(lex, "RED3", "")
