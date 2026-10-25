"""Edge case tests for recallstorm.rules.red3."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.red3 import evaluate_red3, red3_rules


def test_red3_drug_and_cosmetic_scope():
    rules = red3_rules()
    drug = Sku("D1", "00012345678905", "Pills", "B", "drug", "FD&C RED NO. 3", False, True, 12, 1.0, 5.0)
    # In 2027, ingested drug is still allowed!
    assert evaluate_red3(drug, rules, "CA", datetime(2027, 6, 1)).verdict == Verdict.KEEP
    # In Feb 2028, ingested drug is prohibited!
    assert evaluate_red3(drug, rules, "CA", datetime(2028, 2, 1)).verdict == Verdict.PULL

    cosm = Sku("C1", "00012345678905", "Lipstick", "B", "cosmetic", "FD&C RED NO. 3", False, False, 12, 1.0, 5.0)
    assert evaluate_red3(cosm, rules, "CA", datetime(2029, 1, 1)).verdict == Verdict.KEEP
