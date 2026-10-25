"""Property tests for recallstorm.adjudicate.evidence."""
from datetime import datetime
from contract import Sku
from recallstorm.adjudicate.evidence import build_evidence, validate_evidence
from recallstorm.rules.engine import evaluate_sku
from recallstorm.rules.red3 import red3_aliases, red3_rules


def test_evidence_schema_validity_props():
    rules = red3_rules()
    t = datetime.fromisoformat("2027-01-01T00:00:00-08:00")
    for i, al in enumerate(red3_aliases()):
        sku = Sku(f"S{i}", "00012345678905", "Item", "B", "candy", f"WATER, {al}, SUGAR", True, False, 12, 1.0, 5.0)
        dec = evaluate_sku(sku, rules, "CA", t)
        ev = build_evidence(sku, dec, rules[0])
        assert validate_evidence(ev) == []
