"""Property tests for recallstorm.rules.scope."""
from contract import Rule, Sku
from datetime import datetime
from recallstorm.rules.scope import exclude_reason, sku_in_scope


def test_scope_and_exclude_reason_complement():
    r_food = Rule("R_FOOD", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "c", "t")
    for is_f in (True, False):
        for is_d in (True, False):
            sku = Sku("S", "00012345678905", "N", "B", "c", "I", is_f, is_d, 12, 1.0, 5.0)
            assert sku_in_scope(sku, r_food) == (exclude_reason(sku, r_food) is None)
