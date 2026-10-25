"""Edge case tests for recallstorm.rules.bvo."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.bvo import evaluate_bvo_federal


def test_bvo_edge():
    sku = Sku("BV1", "00012345678905", "Citrus Soda", "B", "beverage", "WATER, BVO", True, False, 12, 1.0, 5.0)
    assert evaluate_bvo_federal(sku, "US", datetime(2025, 1, 1)).verdict == Verdict.KEEP
    dec_ca_2027 = evaluate_bvo_federal(sku, "CA", datetime(2027, 1, 2))
    assert "CA_AB418_BVO" in dec_ca_2027.rule_ids
