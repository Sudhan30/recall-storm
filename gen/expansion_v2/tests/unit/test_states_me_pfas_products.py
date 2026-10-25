"""Unit tests for recallstorm.states.me_pfas_products."""
from recallstorm.states.me_pfas_products import (
    MeCuuExemptionCheck,
    MePfasReportingRule,
    build_me_vendor_disclosure_request,
    calculate_me_reporting_fee_tier,
    check_me_intentionally_added_pfas,
    evaluate_me_cookware_coating_skus,
    filter_me_housewares_planogram,
    flag_me_unreported_fabric_sprays,
    generate_me_sales_prohibition_list,
    parse_me_title_38_section_1614,
    validate_me_cas_registry_match,
    verify_me_dep_notification_id,
)


def test_me_pfas_products():
    assert MePfasReportingRule().status == "ACTIVE"
    assert MeCuuExemptionCheck().status == "ACTIVE"
    assert verify_me_dep_notification_id("DEP-1")["verified"] is True
    assert check_me_intentionally_added_pfas("PTFE COATING")["has_pfas"] is True
    assert evaluate_me_cookware_coating_skus("S1", True)["prohibited"] is True
    assert flag_me_unreported_fabric_sprays(["S2", "S1"]) == ["S1", "S2"]
    assert calculate_me_reporting_fee_tier(4, 250.0) == 1000.0
    assert parse_me_title_38_section_1614("Maine PFAS law")["state"] == "ME"
    assert build_me_vendor_disclosure_request("V1", "S1")["vendor_id"] == "V1"
    assert filter_me_housewares_planogram(["H1"]) == ["H1"]
    assert validate_me_cas_registry_match("9002-84-0")["is_pfas"] is True
    assert generate_me_sales_prohibition_list(["S1"])["count"] == 1
