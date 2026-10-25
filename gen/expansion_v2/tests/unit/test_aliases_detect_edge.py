"""Edge case tests for recallstorm.aliases.detect."""
from recallstorm.aliases.detect import find_first_match, find_matches


def test_detect_edge():
    assert find_matches("", ("Red 3",), "RED3") == []
    assert find_first_match("SUGAR, WATER", ("Red 3",), "RED3") is None
    # OCR typo should still match with exact slice length
    txt = "SUGAR, REO 3, WATER"
    m = find_first_match(txt, ("Red 3",), "RED3")
    assert m is not None
    assert txt[m.start : m.end] == m.match_text
