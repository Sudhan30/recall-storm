"""Unit tests for recallstorm.rules.ab418."""
from datetime import datetime, timezone
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


def test_ab418_four_additives():
    assert len(AB418_ADDITIVES) == 4
    assert len(ab418_rules()) == 4
    assert ab418_effective().year == 2027
    assert "109025(a)(1)" in ab418_clause("BVO")
    at = datetime(2027, 1, 2, tzinfo=timezone.utc)

    s_bvo = Sku("S1", "00012345678905", "Soda", "B", "beverage", "WATER, BROMINATED VEGETABLE OIL", True, False, 12, 1.0, 5.0)
    s_bro = Sku("S2", "00012345678905", "Bread", "B", "bakery", "BROMATED FLOUR", True, False, 12, 1.0, 5.0)
    s_par = Sku("S3", "00012345678905", "Cake", "B", "bakery", "SUGAR, PROPYLPARABEN", True, False, 12, 1.0, 5.0)
    s_red = Sku("S4", "00012345678905", "Candy", "B", "candy", "SUGAR, RED DYE 3", True, False, 12, 1.0, 5.0)

    d1 = evaluate_bvo(s_bvo, at)
    d2 = evaluate_potassium_bromate(s_bro, at)
    d3 = evaluate_propylparaben(s_par, at)
    d4 = evaluate_red3_ca(s_red, at)
    assert all(d.verdict == Verdict.PULL for d in (d1, d2, d3, d4))
    summary = ab418_summary([d1, d2, d3, d4])
    assert summary["total_pulled"] == 4
