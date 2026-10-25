"""Edge case tests for recallstorm.adjudicate.evidence."""
from contract import DecidedBy, Sku, SkuDecision, Verdict
from recallstorm.adjudicate.evidence import evidence_span, highlight_match, source_excerpt, validate_evidence


def test_evidence_edge():
    sku = Sku("S1", "00012345678905", "Candy", "B", "candy", "SUGAR, ARTIFICIAL COLOR", True, False, 12, 1.0, 5.0)
    dec = SkuDecision("S1", Verdict.HOLD_VERIFY, "RED3", None, None, None, ("CA_AB418_RED3",), DecidedBy.RULE, "Unclear")
    sp = evidence_span(sku, dec)
    assert sp["start"] == 0
    assert source_excerpt("", None, None) == ""
    assert highlight_match("ABC", None, None) == "ABC"
    assert len(validate_evidence({"type": "evidence"})) > 0
