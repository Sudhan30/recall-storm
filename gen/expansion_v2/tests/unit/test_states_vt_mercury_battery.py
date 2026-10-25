"""Unit tests for recallstorm.states.vt_mercury_battery."""
from recallstorm.states.vt_mercury_battery import (
    VtButtonCellBanCheck,
    VtExtendedProducerRule,
    audit_vt_seasonal_toy_shipments,
    build_vt_endcap_battery_pull,
    calculate_vt_recycling_surcharge,
    check_vt_alkaline_mercury_ppm,
    evaluate_vt_embedded_battery_skus,
    filter_vt_electronics_blister_packs,
    flag_vt_non_compliant_greeting_cards,
    parse_vt_anr_brand_directory,
    validate_vt_packaging_symbol_mark,
    verify_vt_stewardship_plan_membership,
)


def test_vt_mercury_battery():
    assert VtExtendedProducerRule().status == "ACTIVE"
    assert VtButtonCellBanCheck().status == "ACTIVE"
    assert verify_vt_stewardship_plan_membership("Duracell", True)["compliant"] is True
    assert check_vt_alkaline_mercury_ppm(5.0, 0.0)["prohibited"] is True
    assert evaluate_vt_embedded_battery_skus("S1", True)["compliant"] is True
    assert flag_vt_non_compliant_greeting_cards(["S2", "S1"]) == ["S1", "S2"]
    assert parse_vt_anr_brand_directory("DIR1")["state"] == "VT"
    assert build_vt_endcap_battery_pull("WM1", "S1")["sku_id"] == "S1"
    assert filter_vt_electronics_blister_packs(["S1"]) == ["S1"]
    assert calculate_vt_recycling_surcharge(10, 0.15) == 1.5
    assert validate_vt_packaging_symbol_mark("0% Hg Mercury Free")["valid"] is True
    assert audit_vt_seasonal_toy_shipments("WM1", 2)["shipments_checked"] == 2
