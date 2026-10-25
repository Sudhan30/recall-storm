"""Edge case tests for recallstorm.rules.scope."""
from datetime import datetime
from contract import Rule, Sku
from recallstorm.rules.scope import applies_to_sku, exclude_reason


def test_rules_scope_edge():
    food = Sku("F1", "00012345678905", "Candy", "B", "candy", "RED 3", True, False, 12, 1.0, 5.0)
    r_food = Rule("R_FOOD", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "c", "t")
    assert exclude_reason(food, r_food) is None
    assert not applies_to_sku(r_food, food, "NY", datetime(2027, 1, 1))
