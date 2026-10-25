"""Property tests for recallstorm.states.il_food_safety_act."""
from recallstorm.states.il_food_safety_act import check_il_sb2637_scope


def test_il_sb2637_four_additives_in_scope():
    for add in ("BVO", "POTASSIUM_BROMATE", "PROPYLPARABEN", "RED3"):
        assert check_il_sb2637_scope(add, True)["in_scope"] is True
        assert check_il_sb2637_scope(add, False)["in_scope"] is False
