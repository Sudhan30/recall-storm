"""Property tests for recallstorm.pricing.register_prompts."""
from recallstorm.pricing.register_prompts import capture_cashier_entered_lot_string


def test_entered_lot_matching_props():
    for i in range(15):
        res = capture_cashier_entered_lot_string(f"L26{i:02d}", ["L26*"])
        assert res["sale_blocked"] is True
