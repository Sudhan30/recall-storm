"""Edge case tests for recallstorm.adjudicate.overrides."""
import pytest
from contract import DecidedBy, SkuDecision, Verdict
from recallstorm.adjudicate.overrides import Override, apply_override, validate_override


def test_overrides_edge():
    bad = Override("", Verdict.KEEP, "BAD_REASON", "")
    assert len(validate_override(bad)) == 3
    dec = SkuDecision("S1", Verdict.HOLD_VERIFY, "RED3", None, None, None, (), DecidedBy.RULE, "")
    ov = Override("S2", Verdict.KEEP, "LAB_COA_VERIFIED", "qa")
    with pytest.raises(ValueError):
        apply_override(dec, ov)
