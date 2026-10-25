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
    s1 = "SUGAR, CORN SYRUP, FD&C RED #3, FD&C RED #40, SALT."
    m = find_first_match(s1, ("FD&C Red No. 3", "Red 3", "E127"), "RED3")
    assert isinstance(m, MatchResult)
    assert s1[m.start : m.end] == m.match_text
    assert "RED #3" in m.match_text
    assert match_confidence(m) == 1.0
    sp = match_span(m)
    assert sp.text == m.match_text
    assert "RED3" in explain_match(m)

    s2 = "NONPAREILS (SUGAR, CORNSTARCH, E127, RED 40)"
    m2 = find_first_match(s2, ("E127",), "RED3")
    assert m2 is not None and m2.match_text == "E127"

    all_m = detect_all_additives("SUGAR, E127, POTASSIUM BROMATE, BVO")
    adds = {x.additive for x in all_m}
    assert {"RED3", "POTASSIUM_BROMATE", "BVO"}.issubset(adds)


def test_decoys_rejected():
    decoy_text = "WATER, FD&C RED #40, D&C RED #33, 3 PEPPER, RED PEPPER."
    assert find_matches(decoy_text, ("FD&C Red No. 3", "Red 3", "E127"), "RED3") == []
    assert is_decoy("D&C RED 3", 4, 9, "RED3")
    assert decoy_reason("D&C RED 3", 4, 9, "RED3") is not None
