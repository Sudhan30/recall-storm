"""Unit tests for recallstorm.rules.scope."""
from datetime import datetime
from contract import Rule, Sku
from recallstorm.rules.scope import (
    applies_to_sku,
    exclude_reason,
    is_cosmetic_scope,
    is_drug_scope,
    is_food_scope,
    product_types_for_sku,
    scope_matrix,
    scope_reason,
    sku_in_scope,
)


def test_rules_scope():
    food = Sku("F1", "00012345678905", "Candy", "B", "candy", "RED 3", True, False, 12, 1.0, 5.0)
    drug = Sku("D1", "00012345678912", "Cough Syrup", "B", "drug", "RED 3", False, True, 12, 1.0, 5.0)
    cosm = Sku("C1", "00012345678929", "Lipstick", "B", "cosmetic", "RED 3", False, False, 12, 1.0, 5.0)
    r_food = Rule("R_FOOD", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "c", "t")
    r_drug = Rule("R_DRUG", "RED3", ("Red 3",), ("US",), ("ingested_drug",), datetime(2028, 1, 18), "c", "t")

    assert is_food_scope(food) and not is_drug_scope(food)
    assert is_drug_scope(drug) and not is_food_scope(drug)
    assert is_cosmetic_scope(cosm)
    assert product_types_for_sku(food) == ("food",)
    assert sku_in_scope(food, r_food) is True
    assert sku_in_scope(drug, r_food) is False
    assert exclude_reason(drug, r_food) is not None
    assert "in scope" in scope_reason(food, r_food)
    assert applies_to_sku(r_food, food, "CA", datetime(2027, 1, 1)) is True
    assert applies_to_sku(r_drug, drug, "CA", datetime(2027, 6, 1)) is False
    mat = scope_matrix([food, drug, cosm], [r_food, r_drug])
    assert mat["F1"] == ["R_FOOD"] and mat["D1"] == ["R_DRUG"] and mat["C1"] == []
