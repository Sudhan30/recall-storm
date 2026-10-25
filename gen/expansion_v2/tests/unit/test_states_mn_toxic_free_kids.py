"""Unit tests for recallstorm.states.mn_toxic_free_kids."""
from recallstorm.states.mn_toxic_free_kids import (
    MnLeadCadmiumBan,
    MnPriorityChemicalRule,
    audit_mn_vendor_test_reports,
    build_mn_merchant_stop_sale,
    calculate_mn_surface_coating_limit,
    check_mn_toy_jewelry_ppm,
    evaluate_mn_child_mouthable_item,
    filter_mn_checklane_impulses,
    flag_mn_seasonal_novelty_skus,
    generate_mn_disposal_manifest,
    parse_mn_statute_325f_177,
    verify_mn_mdh_waiver_status,
)


def test_mn_toxic_free_kids():
    assert MnPriorityChemicalRule().status == "ACTIVE"
    assert MnLeadCadmiumBan().status == "ACTIVE"
    assert check_mn_toy_jewelry_ppm(100.0, 20.0)["prohibited"] is True
    assert check_mn_toy_jewelry_ppm(50.0, 80.0)["prohibited"] is True
    assert evaluate_mn_child_mouthable_item(3.5)["mouthable"] is True
    assert verify_mn_mdh_waiver_status("S1", False)["waived"] is False
    assert flag_mn_seasonal_novelty_skus("seasonal toy")["flagged"] is True
    assert calculate_mn_surface_coating_limit(40.0, 90.0)["compliant"] is True
    assert parse_mn_statute_325f_177("Minn Stat")["state"] == "MN"
    assert build_mn_merchant_stop_sale("WM1", "S1")["sku_id"] == "S1"
    assert filter_mn_checklane_impulses(["S2", "S1"]) == ["S1", "S2"]
    assert audit_mn_vendor_test_reports("V1", 2)["reports_count"] == 2
    assert generate_mn_disposal_manifest("WM1", 5)["units"] == 5
