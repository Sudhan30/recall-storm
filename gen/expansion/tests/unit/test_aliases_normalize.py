"""Unit tests for recallstorm.aliases.normalize."""
from recallstorm.aliases.normalize import (
    collapse_whitespace,
    denormalize_span,
    fold_unicode,
    ingredient_offsets,
    normalize_ingredients,
    ocr_fix,
    split_sub_ingredients,
    strip_punctuation,
    tokenize_ingredients,
)


def test_normalize_functions():
    raw = "SUGAR,  CHERRIES (COLORED WITH El27,  érythrosine)."
    assert "E127" in ocr_fix(raw)
    assert "erythrosine" in fold_unicode(raw)
    assert "  " not in collapse_whitespace(raw)
    assert "." not in strip_punctuation(raw)
    norm = normalize_ingredients(raw)
    assert "E127" in norm and "ERYTHROSINE" in norm
    assert len(tokenize_ingredients("A, B; C")) == 3
    subs = split_sub_ingredients(raw)
    assert "SUGAR" in subs
    offs = ingredient_offsets("SUGAR, FD&C RED #3.")
    assert offs[1] == ("FD&C RED #3", 7, 18)
    assert denormalize_span("ABC", 0, 2) == (0, 2)
