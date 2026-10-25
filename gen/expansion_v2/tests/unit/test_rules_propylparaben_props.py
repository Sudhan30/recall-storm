"""Property tests for recallstorm.rules.propylparaben."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.propylparaben import evaluate_propylparaben, paraben_aliases


def test_propylparaben_aliases_props():
    for al in paraben_aliases():
        sku = Sku("P1", "00012345678905", "Pastry", "B", "bakery", f"SUGAR, {al}, SALT", True, False, 12, 1.0, 5.0)
        dec = evaluate_propylparaben(sku, "CA", datetime(2027, 1, 1))
        assert dec.verdict == Verdict.PULL
