"""Unit tests for recallstorm.states.ny_dietary_supplements."""
from recallstorm.states.ny_dietary_supplements import (
    NySupplementAgeGate,
    WeightLossClaimMatcher,
    audit_ny_self_checkout_block,
    check_ny_delivery_age_gate,
    classify_ny_thermogenic_sku,
    flag_creatine_products,
    generate_ny_ag_notice,
    is_restricted_ny_supplement,
    map_ny_supplement_aisles,
    scan_muscle_building_claims,
    validate_ny_courier_handoff,
    verify_ny_pos_id_prompt,
)


def test_ny_dietary_supplements():
    assert NySupplementAgeGate().status == "ACTIVE"
    assert WeightLossClaimMatcher().status == "ACTIVE"
    assert is_restricted_ny_supplement("Creatine Monohydrate Muscle Building") is True
    assert verify_ny_pos_id_prompt("S1", 19)["allowed"] is True
    assert verify_ny_pos_id_prompt("S1", 16)["allowed"] is False
    assert scan_muscle_building_claims("Rapid Fat Burner")["flagged"] is True
    assert flag_creatine_products([{"sku_id": "S1", "name": "Creatine Powder"}]) == ["S1"]
    assert check_ny_delivery_age_gate("ORD1", True)["compliant"] is True
    assert audit_ny_self_checkout_block("WM1", 2)["override_count"] == 2
    assert classify_ny_thermogenic_sku("S1", "thermogenic blend")["restricted"] is True
    assert generate_ny_ag_notice("WM1", ["S1"])["count"] == 1
    assert map_ny_supplement_aisles("WM1", ["H02", "H01"])["aisles"] == ["H01", "H02"]
    assert validate_ny_courier_handoff("HND1", True)["valid"] is True
