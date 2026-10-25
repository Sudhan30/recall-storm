"""Unit tests for recallstorm.states.tx_consumable_hemp."""
from recallstorm.states.tx_consumable_hemp import (
    DshsHempRegistration,
    TxHempRetailRule,
    audit_tx_license_expiration,
    calculate_tx_hemp_tax_hold,
    check_tx_child_resistant_cap,
    check_tx_delta9_thc_pct,
    evaluate_tx_smokeable_ban,
    filter_tx_beverage_endcaps,
    flag_tx_unregistered_brands,
    generate_tx_dshs_audit_log,
    validate_tx_batch_coa_date,
    verify_tx_qr_code_link,
)


def test_tx_consumable_hemp():
    assert TxHempRetailRule().status == "ACTIVE"
    assert DshsHempRegistration().status == "ACTIVE"
    assert check_tx_delta9_thc_pct(0.25)["compliant"] is True
    assert check_tx_delta9_thc_pct(0.45)["compliant"] is False
    assert verify_tx_qr_code_link("https://coa.example.com/1")["valid"] is True
    assert validate_tx_batch_coa_date("2026-06-01")["valid"] is True
    assert evaluate_tx_smokeable_ban("pre-roll flower")["prohibited"] is True
    assert flag_tx_unregistered_brands("UnknownBrand")["flagged"] is True
    assert check_tx_child_resistant_cap("S1", True)["compliant"] is True
    assert filter_tx_beverage_endcaps(["S2", "S1"]) == ["S1", "S2"]
    assert generate_tx_dshs_audit_log("WM1", 5)["skus_checked"] == 5
    assert calculate_tx_hemp_tax_hold(10, 15.0) == 150.0
    assert audit_tx_license_expiration("WM1", "2027-06-01")["active"] is True
