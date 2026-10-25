"""Unit tests for recallstorm.states.wv_kratom_hemp_act."""
from recallstorm.states.wv_kratom_hemp_act import (
    WvAgeVerificationMandate,
    WvSelectPlantRule,
    audit_wv_display_case_locks,
    build_wv_seizure_readiness_pack,
    calculate_wv_unregistered_penalty,
    check_wv_mitragynine_limit,
    check_wv_warning_statement_box,
    evaluate_wv_synthetic_alkaloids,
    filter_wv_c_store_formats,
    flag_wv_adulterated_tinctures,
    validate_wv_lab_accreditation,
    verify_wv_wvda_product_permit,
)


def test_wv_kratom_hemp_act():
    assert WvSelectPlantRule().status == "ACTIVE"
    assert WvAgeVerificationMandate().status == "ACTIVE"
    assert check_wv_mitragynine_limit(1.5, 2.0)["compliant"] is True
    assert evaluate_wv_synthetic_alkaloids("synthetic 7-OH")["prohibited"] is True
    assert verify_wv_wvda_product_permit("S1", True)["registered"] is True
    assert flag_wv_adulterated_tinctures(["S2", "S1"]) == ["S1", "S2"]
    assert check_wv_warning_statement_box("Warning: Must be 21")["compliant"] is True
    assert filter_wv_c_store_formats(["WM1"]) == ["WM1"]
    assert build_wv_seizure_readiness_pack("WM1", 3)["sku_count"] == 3
    assert calculate_wv_unregistered_penalty(5, 100.0) == 500.0
    assert validate_wv_lab_accreditation("LAB1", True)["valid"] is True
    assert audit_wv_display_case_locks("WM1", True)["compliant"] is True
