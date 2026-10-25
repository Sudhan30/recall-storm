"""Integration test 08: OCR label -> Unclear detection -> Rule evaluation -> Classifier -> ReviewQueue -> Override -> Audit."""
from datetime import datetime, timezone
from contract import Sku, Verdict
from recallstorm.adjudicate import (
    AuditTrail,
    HeuristicClassifier,
    Override,
    ReviewQueue,
    apply_override,
    enqueue,
    mark_reviewed,
    record_decision,
    record_override,
)
from recallstorm.aliases import needs_human_review
from recallstorm.core import make_evidence_id
from recallstorm.ingest import ocr_to_ingredients, parse_ocr_payload
from recallstorm.rules import evaluate_sku, red3_rules


def test_flow_08_adjudicate_workflow():
    ocr = parse_ocr_payload(
        {
            "sku_id": "OCR_SKU1",
            "blocks": ["INGREDIENTS: SUGAR, CORN SYRUP, ARTIFICIAL COLOR."],
            "confidence": 0.88,
        }
    )
    ing = ocr_to_ingredients(ocr)
    assert needs_human_review(ing) is True

    sku = Sku("OCR_SKU1", "00012345678905", "Mystery Candy", "B", "candy", ing, True, False, 12, 1.0, 5.0)
    rules = red3_rules()
    clf = HeuristicClassifier()
    dec = evaluate_sku(sku, rules, "CA", datetime(2027, 1, 2, tzinfo=timezone.utc), classifier=clf)
    assert dec.verdict == Verdict.HOLD_VERIFY
    assert make_evidence_id(sku.sku_id, "CA_AB418_RED3").startswith("EVD-")

    q = ReviewQueue()
    enqueue(q, {"sku_id": sku.sku_id, "store_id": "WM1563", "reason": dec.rationale})
    assert mark_reviewed(q, sku.sku_id, Verdict.KEEP, "compliance_lead") is True

    ov = Override(sku.sku_id, Verdict.KEEP, "VENDOR_COA_VERIFIED", "compliance_lead", "Verified FD&C Red 40 only")
    final_dec = apply_override(dec, ov)
    assert final_dec.verdict == Verdict.KEEP

    trail = AuditTrail()
    record_decision(trail, dec)
    record_override(trail, ov)
    assert len(trail.entries) == 2
