"""Unit tests for recallstorm.aliases.detect."""
from recallstorm.aliases.detect import (
    MatchResult,
    decoy_reason,
    detect_all_additives,
    explain_match,
    find_first_match,
    find_matches,
    is_decoy,
    match_confidence,
    match_span,
)


def test_detect_red3_and_spans():
    ing1 = "SUGAR, CORN SYRUP, FD&C RED #3, FD&C RED #40, SALT."
    m = find_first_match(ing1, "RED3")
    assert isinstance(m, MatchResult)
    assert m.match_text == "FD&C RED #3"
    assert ing1[m.start:m.end] == "FD&C RED #3"
    assert match_span(m).start == m.start
    assert match_confidence(m) == 1.0
    assert "FD&C RED #3" in explain_match(m)

    ing2 = "NONPAREILS (SUGAR, CORNSTARCH, E127, RED 40)."
    m2 = find_first_match(ing2, "RED3")
    assert m2 is not None and m2.match_text == "E127"

    ing3 = "KIT: PINK NONPAREILS (SUGAR, RED 3 POWDER, RED 40 POWDER)."
    m3 = find_first_match(ing3, "RED3")
    assert m3 is not None and m3.match_text == "RED 3 POWDER"

    all_m = detect_all_additives("BROMATED FLOUR, PROPYLPARABEN, FD&C RED #3")
    assert {x.additive for x in all_m} == {"POTASSIUM_BROMATE", "PROPYLPARABEN", "RED3"}


def test_decoys_rejected():
    assert find_matches("SUGAR, FD&C RED #40, RED 40 LAKE.", "RED3") == []
    assert find_matches("D&C RED #33, D&C RED #30, WATER.", "RED3") == []
    assert find_matches("BEEF, NATURAL FLAVORS (JALAPENO, RED PEPPER), 3 RED BELL PEPPERS.", "RED3") == []
    assert is_decoy("D&C RED #3", 4, 10, "RED3") is True
    assert decoy_reason("D&C RED #3", 4, 10) is not None
