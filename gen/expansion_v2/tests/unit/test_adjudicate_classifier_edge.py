"""Edge case tests for recallstorm.adjudicate.classifier."""
import json
from contract import Sku, Verdict
from recallstorm.adjudicate.classifier import parse_classifier_reply
from recallstorm.rules.red3 import red3_rules


def test_classifier_edge():
    rules = red3_rules()[:1]
    sku = Sku("S1", "00012345678905", "Candy", "B", "candy", "SUGAR", True, False, 12, 1.0, 5.0)
    assert parse_classifier_reply("", sku, rules).verdict == Verdict.HOLD_VERIFY
    assert parse_classifier_reply("not json", sku, rules).verdict == Verdict.HOLD_VERIFY
    low_conf = json.dumps({"verdict": "KEEP", "confidence": 0.4})
    assert parse_classifier_reply(low_conf, sku, rules).verdict == Verdict.HOLD_VERIFY
