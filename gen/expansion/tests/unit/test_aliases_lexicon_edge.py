"""Edge tests for recallstorm.aliases.lexicon."""
import pytest
from recallstorm.aliases.lexicon import (
    add_alias,
    additive_for_alias,
    aliases_for,
    load_lexicon,
)


def test_lexicon_edge():
    lex = load_lexicon()
    assert additive_for_alias("", lex) is None
    assert additive_for_alias("NotAnAdditive", lex) is None
    assert aliases_for("UNKNOWN_ADDITIVE", lex) == ()
    with pytest.raises(ValueError):
        aliases_for("")
    with pytest.raises(ValueError):
        add_alias(lex, "", "x")
