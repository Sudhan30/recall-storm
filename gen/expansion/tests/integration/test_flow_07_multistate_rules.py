"""Integration test 07: Multi-state regulatory rules (CA AB418, FDA BVO, MN PFAS, CARB VOC, preemption, audit)."""
from datetime import datetime, timezone
from contract import Sku, Verdict
from recallstorm.adjudicate import AuditTrail, record_decision, verify_audit
from recallstorm.aliases import detect_all_additives
from recallstorm.core import to_local
from recallstorm.rules import (
    ab418_rules,
    bvo_rules,
    carb_voc_rules,
    evaluate_pfas,
    evaluate_sku,
    evaluate_voc,
    pfas_rules,
    preemption_report,
)


def test_flow_07_multistate_rules():
    at = to_local(datetime(2027, 1, 2, 12, 0, tzinfo=timezone.utc), "America/Los_Angeles")
    rules = ab418_rules() + bvo_rules() + pfas_rules() + carb_voc_rules()
    rep = preemption_report(rules, "CA")
    assert "BVO" in rep["additives"]

    s_bvo = Sku("BVO1", "00012345678905", "Citrus Soda", "B", "beverage", "WATER, SUGAR, BVO", True, False, 12, 1.0, 5.0)
    s_pfas = Sku("PF1", "00012345678912", "Nonstick Pan", "B", "cookware", "ALUMINUM, PTFE", False, False, 6, 2.0, 10.0)
    s_voc = Sku("VOC1", "00012345678929", "Multi-Purpose Lubricant", "B", "lubricant", "DISTILLATES, VOC: 18%", False, False, 12, 1.0, 8.0)

    assert len(detect_all_additives(s_bvo.ingredients)) == 1
    d_bvo = evaluate_sku(s_bvo, rules, "TX", at)
    assert d_bvo.verdict == Verdict.PULL and "FDA_BVO_FOOD" in d_bvo.rule_ids

    d_pfas_mn = evaluate_pfas(s_pfas, "MN", at)
    d_pfas_tx = evaluate_pfas(s_pfas, "TX", at)
    assert d_pfas_mn.verdict == Verdict.PULL
    assert d_pfas_tx.verdict == Verdict.KEEP

    d_voc = evaluate_voc(s_voc, "CA", at)
    assert d_voc.verdict == Verdict.PULL

    trail = AuditTrail()
    for d in (d_bvo, d_pfas_mn, d_voc):
        record_decision(trail, d, at)
    assert verify_audit(trail) is True
