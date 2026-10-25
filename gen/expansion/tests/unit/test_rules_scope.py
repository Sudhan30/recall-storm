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


def test_scope_evaluation():
    food_sku = Sku("F1", "00012345678905", "Candy", "B", "candy", "SUGAR", True, False, 12, 1.0, 5.0)
    drug_sku = Sku("D1", "00012345678912", "Syrup", "B", "cough", "RED 3", False, True, 12, 1.0, 5.0)
    cosm_sku = Sku("C1", "00012345678929", "Lipstick", "B", "cosmetic", "RED 3", False, False, 12, 1.0, 5.0)

    r_food = Rule("R_F", "RED3", ("Red 3",), ("CA",), ("food",), datetime(2027, 1, 1), "c", "s")
    r_drug = Rule("R_D", "RED3", ("Red 3",), ("US",), ("ingested_drug",), datetime(2028, 1, 18), "c", "s")

    assert is_food_scope(food_sku) is True
    assert is_drug_scope(drug_sku) is True
    assert is_cosmetic_scope(cosm_sku) is True
    assert product_types_for_sku(food_sku) == ("food",)
    assert sku_in_scope(food_sku, r_food) is True
    assert applies_to_sku(r_food, drug_sku) is False
    assert exclude_reason(food_sku, r_food) is None
    assert exclude_reason(drug_sku, r_food) is not None
    assert "match" in scope_reason(food_sku, r_food)
    mat = scope_matrix([food_sku, drug_sku, cosm_sku], [r_food, r_drug])
    assert mat["F1"] == ["R_F"]
    assert mat["D1"] == ["R_D"]
    assert mat["C1"] == []
