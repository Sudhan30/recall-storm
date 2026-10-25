"""Unit tests for recallstorm.states.ut_cotinine_nicotine."""
from recallstorm.states.ut_cotinine_nicotine import (
    UtElectronicCigaretteRule,
    UtSpecialtyPermitCheck,
    audit_ut_age_scanner_logs,
    build_ut_cage_removal_task,
    calculate_ut_revocation_risk,
    check_ut_nicotine_volume_cap,
    evaluate_ut_flavor_restriction,
    filter_ut_front_end_fixtures,
    flag_ut_unauthorized_vape_skus,
    parse_ut_dhhs_banned_list,
    validate_ut_wholesaler_invoice,
    verify_ut_tax_stamp_presence,
)


def test_ut_cotinine_nicotine():
    assert UtElectronicCigaretteRule().status == "ACTIVE"
    assert UtSpecialtyPermitCheck().status == "ACTIVE"
    assert check_ut_nicotine_volume_cap(24.0, 36.0)["compliant"] is True
    assert evaluate_ut_flavor_restriction("mango", False)["allowed"] is False
    assert evaluate_ut_flavor_restriction("menthol", False)["allowed"] is True
    assert verify_ut_tax_stamp_presence("S1", True)["compliant"] is True
    assert flag_ut_unauthorized_vape_skus(["S2", "S1"]) == ["S1", "S2"]
    assert parse_ut_dhhs_banned_list("N1")["state"] == "UT"
    assert build_ut_cage_removal_task("WM1", "S1")["sku_id"] == "S1"
    assert filter_ut_front_end_fixtures(["F1"]) == ["F1"]
    assert calculate_ut_revocation_risk(3)["high_risk"] is True
    assert validate_ut_wholesaler_invoice("INV1", True)["valid"] is True
    assert audit_ut_age_scanner_logs("WM1", 99.5)["compliant"] is True
