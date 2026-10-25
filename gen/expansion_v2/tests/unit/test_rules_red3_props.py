"""Property tests for recallstorm.rules.red3."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.red3 import evaluate_red3, red3_aliases, red3_evidence, red3_rules
from recallstorm.aliases.detect import find_first_match


def test_red3_evidence_spans():
    rules = red3_rules()
    for al in red3_aliases():
        sku = Sku("S1", "00012345678905", "Candy", "B", "candy", f"SUGAR, {al}, WATER", True, False, 12, 1.0, 5.0)
        dec = evaluate_red3(sku, rules, "CA", datetime(2027, 1, 1))
        assert dec.verdict == Verdict.PULL
        m = find_first_match(sku.ingredients, red3_aliases(), "RED3")
        assert m is not None
        ev = red3_evidence(sku, rules[0], m)
        assert ev["source_span"]["text"] == dec.match_text
