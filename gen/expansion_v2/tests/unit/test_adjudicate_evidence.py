"""Unit tests for recallstorm.adjudicate.evidence."""
from datetime import datetime
from contract import Sku
from recallstorm.adjudicate.evidence import (
    build_evidence,
    evidence_card,
    evidence_index,
    evidence_span,
    evidence_to_record,
    highlight_match,
    link_evidence,
    source_excerpt,
    validate_evidence,
)
from recallstorm.rules.engine import decision_to_record, evaluate_sku
from recallstorm.rules.red3 import red3_rules


def test_evidence_generation():
    rules = red3_rules()
    sku = Sku("FDC1034191", "07502264930572", "Sprinkles", "B", "baking", "SUGAR, FD&C RED #3, SALT.", True, False, 6, 2.0, 10.0)
    dec = evaluate_sku(sku, rules, "CA", datetime.fromisoformat("2027-01-01T00:00:00-08:00"))
    ev = build_evidence(sku, dec, rules[0])
    assert validate_evidence(ev) == []
    assert evidence_span(sku, dec)["text"] == "FD&C RED #3"
    assert "FD&C RED #3" in source_excerpt(sku.ingredients, dec.match_start, dec.match_end)
    assert "[FD&C RED #3]" in highlight_match(sku.ingredients, dec.match_start, dec.match_end)
    assert "EVD-" in evidence_card(ev)
    assert evidence_to_record(ev)["type"] == "evidence"
    v_rec = decision_to_record(sku, dec, rules)
    linked = link_evidence(v_rec, ev)
    assert linked["evidence_id"] == ev["evidence_id"]
    idx = evidence_index([ev])
    assert ev["evidence_id"] in idx
