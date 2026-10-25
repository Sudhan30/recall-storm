"""Unit tests for recallstorm.states.pa_synthetic_dyes."""
from recallstorm.states.pa_synthetic_dyes import (
    PaSchoolDyeRule,
    PaSyntheticDyeList,
    audit_pa_confectionery_endcaps,
    calculate_pa_pack_exposure,
    check_pa_dye_concentration,
    evaluate_pa_school_zone_store,
    filter_pa_vending_inventory,
    flag_red40_yellow5_skus,
    generate_pa_parent_advisory,
    map_pa_affected_categories,
    validate_pa_catering_menu,
    verify_pa_warning_label_text,
)


def test_pa_synthetic_dyes():
    assert PaSchoolDyeRule().status == "ACTIVE"
    assert PaSyntheticDyeList().status == "ACTIVE"
    assert check_pa_dye_concentration(75.0, 50.0)["exceeds"] is True
    assert flag_red40_yellow5_skus("SUGAR, RED 40, YELLOW 5")["flagged"] is True
    assert evaluate_pa_school_zone_store("WM1", 400.0)["in_zone"] is True
    assert verify_pa_warning_label_text("Warning: contains synthetic dyes")["compliant"] is True
    assert map_pa_affected_categories("candy")["affected"] is True
    assert calculate_pa_pack_exposure(10, 4) == 40
    assert generate_pa_parent_advisory("WM1", "S1")["sku_id"] == "S1"
    assert filter_pa_vending_inventory(["S2", "S1"]) == ["S1", "S2"]
    assert validate_pa_catering_menu("Lunch", True)["approved"] is True
    assert audit_pa_confectionery_endcaps("WM1", 3)["endcap_count"] == 3
