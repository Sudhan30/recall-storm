"""Unit tests for recallstorm.adjudicate.classifier."""
import json
from contract import Sku, Verdict
from recallstorm.adjudicate.classifier import (
    ClassifierStats,
    GeminiClassifier,
    HeuristicClassifier,
    batch_classify,
    classifier_decision,
    classifier_prompt,
    confidence_threshold,
    fallback_hold,
    parse_classifier_reply,
)
from recallstorm.rules.red3 import red3_rules


def test_classifier():
    rules = red3_rules()[:1]
    sku = Sku("S1", "00012345678905", "Candy", "B", "candy", "SUGAR, ARTIFICIAL COLOR.", True, False, 12, 1.0, 5.0)
    prompt = classifier_prompt(sku, rules)
    assert "CA_AB418_RED3" in prompt
    reply = json.dumps({"verdict": "PULL", "confidence": 0.95, "rationale": "Confirmed Red 3"})
    dec = parse_classifier_reply(reply, sku, rules)
    assert dec.verdict == Verdict.PULL
    assert confidence_threshold(0.85, 0.8) is True
    assert fallback_hold(sku, rules).verdict == Verdict.HOLD_VERIFY
    assert classifier_decision(sku, Verdict.KEEP, "ok", rules).verdict == Verdict.KEEP

    hc = HeuristicClassifier()
    gc = GeminiClassifier()
    assert hc(sku, rules).verdict == Verdict.HOLD_VERIFY
    assert gc(sku, rules).verdict == Verdict.HOLD_VERIFY
    batch = batch_classify([sku], rules, hc)
    assert len(batch) == 1
    stats = ClassifierStats(called=1, holds=1)
    assert stats.holds == 1
