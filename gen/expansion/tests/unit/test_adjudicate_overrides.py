"""Unit tests for recallstorm.adjudicate.overrides."""
from datetime import datetime, timezone
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


def test_overrides_workflow():
    assert "VENDOR_COA_VERIFIED" in override_reason_codes()
    dec = SkuDecision("S1", Verdict.HOLD_VERIFY, "RED3", None, None, None, ("CA_AB418_RED3",), DecidedBy.RULE, "Unclear")
    ov = Override("S1", Verdict.KEEP, "VENDOR_COA_VERIFIED", "alice", "COA states natural beet color", datetime(2027, 6, 1, tzinfo=timezone.utc))
    assert validate_override(ov) == []
    updated = apply_override(dec, ov)
    assert updated.verdict == Verdict.KEEP
    assert updated.rule_ids == ()
    rec = override_to_record(ov)
    assert rec["reviewer"] == "alice"
    assert len(overrides_for_sku([ov], "S1")) == 1
    assert len(expire_overrides([ov], datetime(2027, 1, 1, tzinfo=timezone.utc))) == 1
    assert len(expire_overrides([ov], datetime(2028, 1, 1, tzinfo=timezone.utc))) == 0
    book = OverrideBook([ov])
    assert override_report(book.overrides)["total"] == 1
