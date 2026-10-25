"""Property tests for recallstorm.aliases.lexicon."""
from recallstorm.aliases.lexicon import additive_for_alias, aliases_for, load_lexicon


def test_lexicon_roundtrip_props():
    lex = load_lexicon()
    for add in ("RED3", "BVO", "POTASSIUM_BROMATE", "PROPYLPARABEN"):
        for al in aliases_for(add, lex):
            assert additive_for_alias(al, lex) == add
