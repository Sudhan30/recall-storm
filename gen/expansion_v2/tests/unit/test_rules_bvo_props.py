"""Property tests for recallstorm.rules.bvo."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.bvo import bvo_aliases, evaluate_bvo_federal


def test_bvo_aliases_props():
    for al in bvo_aliases():
        sku = Sku("BV1", "00012345678905", "Soda", "B", "beverage", f"WATER, {al}, CITRIC ACID", True, False, 12, 1.0, 5.0)
        dec = evaluate_bvo_federal(sku, "US", datetime(2026, 6, 1))
        assert dec.verdict == Verdict.PULL
