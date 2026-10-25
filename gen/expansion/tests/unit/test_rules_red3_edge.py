"""Edge tests for recallstorm.rules.red3."""
from datetime import datetime, timezone
from contract import Sku, Verdict
from recallstorm.rules.red3 import evaluate_red3, red3_rules


def test_red3_drug_and_unclear():
    rules = red3_rules()
    drug = Sku("D1", "00012345678905", "Syrup", "B", "drug", "FD&C RED #3", False, True, 12, 1.0, 5.0)
    assert evaluate_red3(drug, rules, "CA", datetime(2027, 6, 1, tzinfo=timezone.utc)).verdict == Verdict.KEEP
    assert evaluate_red3(drug, rules, "CA", datetime(2028, 2, 1, tzinfo=timezone.utc)).verdict == Verdict.PULL

    unclear_sku = Sku("U1", "00012345678905", "Candy", "B", "candy", "SUGAR, ARTIFICIAL COLOR", True, False, 12, 1.0, 5.0)
    assert evaluate_red3(unclear_sku, rules, "CA", datetime(2027, 1, 2, tzinfo=timezone.utc)).verdict == Verdict.HOLD_VERIFY
