"""Unit tests for recallstorm.vendor.onboarding_gates."""
from recallstorm.vendor.onboarding_gates import (
    IngredientScreenBlock,
    NewItemComplianceGate,
    assign_initial_food_safety_risk_tier,
    audit_broker_submitted_onboarding_data,
    check_fda_import_alert_red_list_status,
    enforce_mandatory_epcis_asn_readiness,
    lock_unapproved_sku_from_po_creation,
    reject_unsubstantiated_free_from_claims,
    require_state_specific_regulatory_attestation,
    screen_new_item_setup_for_banned_additives,
    validate_gs1_gtin_lot_coding_capability,
    verify_24_7_emergency_recall_contact_info,
)


def test_onboarding_gates():
    assert NewItemComplianceGate().status == "ACTIVE"
    assert IngredientScreenBlock().status == "ACTIVE"
    res = screen_new_item_setup_for_banned_additives("SUGAR, FD&C RED #3, WATER")
    assert res["blocked"] is True and "RED3" in res["additives"]
    assert require_state_specific_regulatory_attestation("V1", ["CA", "NY"])["states"] == ["CA", "NY"]
    assert validate_gs1_gtin_lot_coding_capability("V1", True)["approved"] is True
    assert verify_24_7_emergency_recall_contact_info("qa@vendor.com", "555-123-4567")["valid"] is True
    assert reject_unsubstantiated_free_from_claims("PFAS-Free", False)["rejected"] is True
    assert check_fda_import_alert_red_list_status("FEI1", {"FEI1"})["red_listed"] is True
    assert enforce_mandatory_epcis_asn_readiness("leafy greens", True)["approved"] is True
    assert assign_initial_food_safety_risk_tier("infant formula") == "HIGH"
    assert audit_broker_submitted_onboarding_data("BRK1", True)["valid"] is True
    assert lock_unapproved_sku_from_po_creation("S1", False)["po_locked"] is True
