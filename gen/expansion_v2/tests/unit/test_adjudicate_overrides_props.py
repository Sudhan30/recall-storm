"""Property tests for recallstorm.adjudicate.overrides."""
from contract import DecidedBy, SkuDecision, Verdict
from recallstorm.adjudicate.overrides import Override, apply_override, override_reason_codes


def test_override_preserves_sku_id():
    for rc in override_reason_codes():
        dec = SkuDecision("S100", Verdict.HOLD_VERIFY, "RED3", None, None, None, ("R1",), DecidedBy.RULE, "r")
        ov = Override("S100", Verdict.PULL, rc, "rev")
        res = apply_override(dec, ov)
        assert res.sku_id == "S100" and res.verdict == Verdict.PULL
