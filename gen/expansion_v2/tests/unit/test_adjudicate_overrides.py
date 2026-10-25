"""Unit tests for recallstorm.adjudicate.overrides."""
from datetime import datetime
from contract import DecidedBy, SkuDecision, Verdict
from recallstorm.adjudicate.overrides import (
    Override,
    OverrideBook,
    apply_override,
    expire_overrides,
    override_reason_codes,
    override_report,
    override_to_record,
    overrides_for_sku,
    validate_override,
)


def test_overrides():
    assert "LAB_COA_VERIFIED" in override_reason_codes()
    ov = Override("S1", Verdict.KEEP, "LAB_COA_VERIFIED", "qa_lead", "Clean COA", datetime(2027, 6, 1))
    assert validate_override(ov) == []
    dec = SkuDecision("S1", Verdict.HOLD_VERIFY, "RED3", None, None, None, ("CA_AB418_RED3",), DecidedBy.RULE, "Unclear")
    updated = apply_override(dec, ov)
    assert updated.verdict == Verdict.KEEP
    assert override_to_record(ov)["reviewer"] == "qa_lead"
    assert len(overrides_for_sku([ov], "S1")) == 1
    assert len(expire_overrides([ov], datetime(2027, 1, 1))) == 1
    assert len(expire_overrides([ov], datetime(2028, 1, 1))) == 0
    assert override_report([ov])["total"] == 1
    book = OverrideBook([ov])
    assert len(book.overrides) == 1
