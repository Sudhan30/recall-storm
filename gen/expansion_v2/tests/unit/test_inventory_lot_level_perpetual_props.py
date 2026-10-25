"""Property tests for recallstorm.inventory.lot_level_perpetual."""
from recallstorm.inventory.lot_level_perpetual import model_fefo_customer_depletion_curve


def test_fefo_curve_non_increasing_props():
    curve = model_fefo_customer_depletion_curve(50, 15, 3.5)
    for i in range(1, len(curve)):
        assert curve[i] <= curve[i - 1]
        assert curve[i] >= 0
