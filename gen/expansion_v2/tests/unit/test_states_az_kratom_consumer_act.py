"""Unit tests for recallstorm.states.az_kratom_consumer_act."""
from recallstorm.states.az_kratom_consumer_act import (
    AzAlkaloidRatioCheck,
    AzKratomStandardRule,
    audit_az_batch_alkaloid_panel,
    build_az_vendor_indemnity_check,
    calculate_az_civil_forfeiture,
    check_az_dosage_instructions,
    evaluate_az_synthetic_adulterants,
    filter_az_wellness_aisle_skus,
    flag_az_confectionery_forms,
    generate_az_stop_sale_notice,
    validate_az_label_disclaimer_text,
    verify_az_7_oh_fraction_limit,
)


def test_az_kratom_consumer_act():
    assert AzKratomStandardRule().status == "ACTIVE"
    assert AzAlkaloidRatioCheck().status == "ACTIVE"
    assert verify_az_7_oh_fraction_limit(1.2, 2.0)["compliant"] is True
    assert check_az_dosage_instructions("Directions: 1 serving daily")["compliant"] is True
    assert evaluate_az_synthetic_adulterants("synthetic alkaloid")["adulterated"] is True
    assert flag_az_confectionery_forms("gummy bears")["flagged"] is True
    assert validate_az_label_disclaimer_text("Contains mitragynine")["valid"] is True
    assert filter_az_wellness_aisle_skus(["S2", "S1"]) == ["S1", "S2"]
    assert build_az_vendor_indemnity_check("V1", True)["valid"] is True
    assert calculate_az_civil_forfeiture(10, 12.0) == 120.0
    assert audit_az_batch_alkaloid_panel("B1", True)["passed"] is True
    assert generate_az_stop_sale_notice("WM1", "S1")["sku_id"] == "S1"
