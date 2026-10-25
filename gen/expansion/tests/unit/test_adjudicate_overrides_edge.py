"""Edge tests for recallstorm.adjudicate.overrides."""
import pytest
from contract import DecidedBy, SkuDecision, Verdict
from recallstorm.adjudicate.overrides import (
    Override,
    apply_override,
    validate_override,
)
from recallstorm.core.errors import DataValidationError


def test_overrides_edge():
    bad = Override("", Verdict.KEEP, "BAD_CODE", "")
    assert len(validate_override(bad)) >= 3
    dec = SkuDecision("S1", Verdict.KEEP, None, None, None, None, (), DecidedBy.RULE, "ok")
    with pytest.raises(DataValidationError):
        apply_override(dec, bad)
    ov_other = Override("S2", Verdict.PULL, "CONFIRMED_POSITIVE_BY_LAB", "bob")
    with pytest.raises(DataValidationError):
        apply_override(dec, ov_other)
