"""Unit tests for recallstorm.rules.ab418."""
from datetime import datetime
from contract import Sku, Verdict
from recallstorm.rules.ab418 import (
    AB418_ADDITIVES,
    ab418_clause,
    ab418_effective,
    ab418_rules,
    ab418_summary,
    evaluate_bvo,
    evaluate_potassium_bromate,
    evaluate_propylparaben,
    evaluate_red3_ca,
)


def test_ab418_all_four_additives():
    assert len(AB418_ADDITIVES) == 4
    assert len(ab418_rules()) == 4
    assert "109025" in ab418_clause()
    t = ab418_effective()

    s_bvo = Sku("S1", "00012345678905", "Soda", "B", "bev", "WATER, BROMINATED VEGETABLE OIL", True, False, 12, 1.0, 5.0)
    s_bro = Sku("S2", "00012345678905", "Bread", "B", "bak", "FLOUR, POTASSIUM BROMATE", True, False, 12, 1.0, 5.0)
    s_par = Sku("S3", "00012345678905", "Cake", "B", "bak", "SUGAR, PROPYLPARABEN", True, False, 12, 1.0, 5.0)
    s_red = Sku("S4", "00012345678905", "Candy", "B", "can", "SUGAR, RED DYE 3", True, False, 12, 1.0, 5.0)

    d1 = evaluate_bvo(s_bvo, "CA", t)
    d2 = evaluate_potassium_bromate(s_bro, "CA", t)
    d3 = evaluate_propylparaben(s_par, "CA", t)
    d4 = evaluate_red3_ca(s_red, "CA", t)
    assert all(d.verdict == Verdict.PULL for d in (d1, d2, d3, d4))
    summ = ab418_summary([d1, d2, d3, d4])
    assert summ["total_pulled"] == 4
