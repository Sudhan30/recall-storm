"""Unit tests for recallstorm.adjudicate.evidence."""
from datetime import datetime, timezone
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
from recallstorm.rules.engine import evaluate_sku
from recallstorm.rules.red3 import red3_rules


def test_evidence_generation():
    rules = red3_rules()
    sku = Sku("FDC1034191", "07502264930572", "Sprinkles", "B", "candy", "SUGAR, FD&C RED #3, SALT", True, False, 6, 2.0, 10.0)
    dec = evaluate_sku(sku, rules, "CA", datetime(2027, 1, 2, tzinfo=timezone.utc))
    assert evidence_span(dec) == [7, 18]
    assert "FD&C RED #3" in source_excerpt(sku.ingredients, 7, 18, 5)
    assert highlight_match(sku.ingredients, 7, 18) == "SUGAR, [FD&C RED #3], SALT"

    ev = build_evidence(sku, dec, rules[0])
    assert validate_evidence(ev) == []
    card = evidence_card(sku, dec, rules[0])
    assert "[FD&C RED #3]" in card["highlighted"]
    strict = evidence_to_record(card)
    assert "highlighted" not in strict
    linked = link_evidence([dec], {r.rule_id: r for r in rules}, {sku.sku_id: sku})
    assert "FDC1034191" in linked
    idx = evidence_index([ev])
    assert ev["evidence_id"] in idx
