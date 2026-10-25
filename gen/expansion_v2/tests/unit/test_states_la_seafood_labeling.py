"""Unit tests for recallstorm.states.la_seafood_labeling."""
from recallstorm.states.la_seafood_labeling import (
    LaCountryOfOriginRule,
    LaImportedShrimpCheck,
    audit_la_service_counter_tags,
    build_la_seafood_case_signage,
    calculate_la_misbranding_fine,
    check_la_crawfish_origin_claim,
    evaluate_la_fluoroquinolone_ban,
    filter_la_frozen_bunker_skus,
    flag_la_unlabeled_bulk_bins,
    parse_la_ldaf_stop_order,
    validate_la_processor_permit,
    verify_la_placard_font_size,
)


def test_la_seafood_labeling():
    assert LaCountryOfOriginRule().status == "ACTIVE"
    assert LaImportedShrimpCheck().status == "ACTIVE"
    assert verify_la_placard_font_size(36, 30)["compliant"] is True
    assert check_la_crawfish_origin_claim("Cajun Crawfish Tails", "CN")["misbranded"] is True
    assert evaluate_la_fluoroquinolone_ban(0.5)["adulterated"] is True
    assert flag_la_unlabeled_bulk_bins(["B2", "B1"]) == ["B1", "B2"]
    assert parse_la_ldaf_stop_order("ORD1")["state"] == "LA"
    assert build_la_seafood_case_signage("WM1", "IMPORTED")["origin"] == "IMPORTED"
    assert calculate_la_misbranding_fine(2, 1500.0) == 3000.0
    assert audit_la_service_counter_tags("WM1", 8)["tags_checked"] == 8
    assert filter_la_frozen_bunker_skus(["S1"]) == ["S1"]
    assert validate_la_processor_permit("PRM1")["valid"] is True
