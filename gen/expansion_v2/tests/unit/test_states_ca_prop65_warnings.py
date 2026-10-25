"""Unit tests for recallstorm.states.ca_prop65_warnings."""
from recallstorm.states.ca_prop65_warnings import (
    AcrylamideExposureCheck,
    Prop65SafeHarborRule,
    audit_prop65_bakery_sign_hooks,
    build_prop65_consent_judgment_rule,
    calculate_prop65_daily_madl_ug,
    check_prop65_bpa_canned_goods,
    evaluate_prop65_short_form_label,
    filter_prop65_unwarned_imports,
    flag_prop65_private_enforcer_notice,
    map_prop65_pos_receipt_warnings,
    parse_oehha_chemical_list_update,
    verify_prop65_shelf_sign_placement,
)


def test_ca_prop65_warnings():
    assert Prop65SafeHarborRule().status == "ACTIVE"
    assert AcrylamideExposureCheck().status == "ACTIVE"
    assert verify_prop65_shelf_sign_placement("WM1", "A01", True)["compliant"] is True
    assert check_prop65_bpa_canned_goods("S1", "BPA Epoxy")["needs_warning"] is True
    assert evaluate_prop65_short_form_label("WARNING: Cancer and Reproductive Harm - www.P65Warnings.ca.gov")["valid"] is True
    assert parse_oehha_chemical_list_update("Lead")["chemical"] == "Lead"
    assert flag_prop65_private_enforcer_notice("NOV-2026-1", "S1")["sku_id"] == "S1"
    assert calculate_prop65_daily_madl_ug(0.8, 0.5)["exceeds_madl"] is True
    assert map_prop65_pos_receipt_warnings("WM1", ["S1", "S2"])["count"] == 2
    assert filter_prop65_unwarned_imports(["S2", "S1"]) == ["S1", "S2"]
    assert build_prop65_consent_judgment_rule("CJ1", 75.0)["max_ppb"] == 75.0
    assert audit_prop65_bakery_sign_hooks("WM1", True)["intact"] is True
