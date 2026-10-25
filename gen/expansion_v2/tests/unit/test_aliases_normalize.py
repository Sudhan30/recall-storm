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
    raw = "Sugar,  Cherries (Water, REO 3, E1Z7), Erythr0sine."
    fixed = ocr_fix(raw)
    assert len(fixed) == len(raw)
    assert "RED 3" in fixed and "E127" in fixed and "ERYTHROSINE" in fixed.upper()
    assert fold_unicode("érythrosine") == "erythrosine"
    assert collapse_whitespace("A   B\n C") == "A B C"
    assert "FD&C" in strip_punctuation("FD&C, RED.")
    assert "RED 3" in normalize_ingredients(raw)
    assert len(tokenize_ingredients("A, B; C.")) == 3
    assert "RED 3" in split_sub_ingredients(fixed)
    offsets = ingredient_offsets(raw)
    for tok, s, e in offsets:
        assert raw[s:e] == tok
    assert denormalize_span("HELLO", (1, 4)) == (1, 4)
