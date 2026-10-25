"""Property tests for recallstorm.rules.potassium_bromate."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.potassium_bromate import bromate_aliases, evaluate_bromate


def test_potassium_bromate_aliases_props():
    for al in bromate_aliases():
        sku = Sku("B1", "00012345678905", "Bread", "B", "bakery", f"FLOUR, {al}, SALT", True, False, 12, 1.0, 5.0)
        dec = evaluate_bromate(sku, "CA", datetime(2027, 1, 1))
        assert dec.verdict == Verdict.PULL
        assert sku.ingredients[dec.match_start : dec.match_end] == dec.match_text
