"""Unit tests for recallstorm.states.nj_lead_cadmium."""
from recallstorm.states.nj_lead_cadmium import (
    NjActionLevelTable,
    NjHeavyMetalRule,
    build_nj_quarantine_tag,
    calculate_nj_daily_intake_exposure,
    check_nj_candy_lead_ppb,
    evaluate_nj_spice_cadmium_limit,
    filter_nj_ethnic_aisle_skus,
    flag_nj_imported_turmeric,
    generate_nj_lab_retest_request,
    parse_nj_doh_embargo_order,
    validate_nj_embargo_release,
    verify_nj_lot_coa_metals,
)


def test_nj_lead_cadmium():
    assert NjHeavyMetalRule().status == "ACTIVE"
    assert NjActionLevelTable().status == "ACTIVE"
    assert check_nj_candy_lead_ppb(150.0, 100.0)["adulterated"] is True
    assert evaluate_nj_spice_cadmium_limit(1.5, 1.0)["exceeds"] is True
    assert parse_nj_doh_embargo_order("ORD1")["state"] == "NJ"
    assert flag_nj_imported_turmeric("Ground Turmeric Powder")["flagged"] is True
    assert verify_nj_lot_coa_metals("L1", 20.0)["passed"] is True
    assert calculate_nj_daily_intake_exposure(10.0, 200.0) == 2.0
    assert build_nj_quarantine_tag("WM1", "S1")["sku_id"] == "S1"
    assert filter_nj_ethnic_aisle_skus(["S2", "S1"]) == ["S1", "S2"]
    assert generate_nj_lab_retest_request("S1", "L1")["lot_id"] == "L1"
    assert validate_nj_embargo_release("REL1", True)["released"] is True
