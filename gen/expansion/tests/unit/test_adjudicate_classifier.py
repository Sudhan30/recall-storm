"""Unit tests for recallstorm.adjudicate.classifier."""
from contract import DecidedBy, Sku, Verdict
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


def test_classifiers():
    rules = red3_rules()[:1]
    s_unclear = Sku("U1", "00012345678905", "Frosting", "B", "baking", "SUGAR, ARTIFICIAL COLOR.", True, False, 12, 1.0, 5.0)
    s_clean = Sku("C1", "00012345678905", "Crackers", "B", "snacks", "WHEAT FLOUR, SALT.", True, False, 12, 1.0, 5.0)

    prompt = classifier_prompt(s_unclear, rules)
    assert "U1" in prompt
    assert confidence_threshold(0.9, 0.85) is True

    hclf = HeuristicClassifier()
    d1 = hclf(s_unclear, rules)
    assert d1.verdict == Verdict.HOLD_VERIFY
    assert d1.decided_by == DecidedBy.MODEL
    assert isinstance(hclf.stats, ClassifierStats) and hclf.stats.holds == 1

    gclf = GeminiClassifier(responder=lambda p: '{"verdict": "KEEP", "rationale": "Verified clean"}')
    d2 = gclf(s_unclear, rules)
    assert d2.verdict == Verdict.KEEP

    batch = batch_classify([s_unclear, s_clean], rules, hclf)
    assert [b.verdict for b in batch] == [Verdict.HOLD_VERIFY, Verdict.KEEP]
    assert fallback_hold(s_unclear, rules).verdict == Verdict.HOLD_VERIFY
    assert classifier_decision(s_clean, rules, Verdict.KEEP, "ok").verdict == Verdict.KEEP
    assert parse_classifier_reply('{"verdict": "PULL", "rationale": "has red 3"}', s_unclear, rules).verdict == Verdict.PULL
