"""Edge tests for recallstorm.adjudicate.classifier."""
import pytest
from contract import Sku, Verdict
from recallstorm.adjudicate.classifier import (
    confidence_threshold,
    parse_classifier_reply,
)
from recallstorm.rules.red3 import red3_rules


def test_classifier_edge():
    rules = red3_rules()[:1]
    sku = Sku("U1", "00012345678905", "Item", "B", "cat", "SUGAR", True, False, 12, 1.0, 5.0)
    assert parse_classifier_reply("not json", sku, rules).verdict == Verdict.HOLD_VERIFY
    assert parse_classifier_reply("", sku, rules).verdict == Verdict.HOLD_VERIFY
    with pytest.raises(ValueError):
        confidence_threshold(0.5, 1.5)
