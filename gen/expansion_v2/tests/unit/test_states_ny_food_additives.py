"""Unit tests for recallstorm.states.ny_food_additives."""
from recallstorm.states.ny_food_additives import (
    NyAdditiveRule,
    TitaniumDioxideCheck,
    build_ny_violation_record,
    calculate_ny_civil_penalty,
    check_ny_ban_date,
    evaluate_tio2_exemption,
    exempt_ny_in_transit_stock,
    filter_ny_store_zips,
    generate_ny_compliance_memo,
    map_ny_ingredient_aliases,
    parse_ny_senate_bill,
    validate_ny_label_claim,
)


def test_ny_food_additives():
    assert NyAdditiveRule().status == "ACTIVE"
    assert TitaniumDioxideCheck().status == "ACTIVE"
    assert check_ny_ban_date("2027-02-01")["prohibited"] is True
    assert evaluate_tio2_exemption("pharmaceutical")["exempt"] is True
    assert parse_ny_senate_bill("Bans titanium dioxide in food")["has_tio2"] is True
    assert build_ny_violation_record("SKU1")["state"] == "NY"
    assert filter_ny_store_zips(["10001", "90210"]) == ["10001"]
    assert "E171" in map_ny_ingredient_aliases("TiO2")
    assert calculate_ny_civil_penalty(3, repeat=True) == 3000.0
    assert exempt_ny_in_transit_stock("BOL1", "NJ")["exempt"] is True
    assert generate_ny_compliance_memo("WM1", 5)["sku_count"] == 5
    assert validate_ny_label_claim("Natural color")["valid"] is True
