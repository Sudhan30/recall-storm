"""Property tests for recallstorm.aliases.normalize."""
from recallstorm.aliases.normalize import fold_unicode, ingredient_offsets, ocr_fix


def test_ocr_fix_and_offsets_length_invariance():
    samples = [
        "SUGAR, REO 3, E1Z7, ERYTHR0SINE",
        "CORN SYRUP, RED N0. 3, EI27, SALT",
        "CHERRIES (WATER, FD&C RED #3, CITRIC ACID)",
    ]
    for s in samples:
        assert len(ocr_fix(s)) == len(s)
        assert len(fold_unicode(s)) == len(s)
        for tok, start, end in ingredient_offsets(s):
            assert s[start:end] == tok
