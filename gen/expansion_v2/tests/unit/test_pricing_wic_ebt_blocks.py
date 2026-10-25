"""Unit tests for recallstorm.pricing.wic_ebt_blocks."""
from recallstorm.pricing.wic_ebt_blocks import (
    EbtEligibilityBlocker,
    WicAplHotfixEngine,
    audit_wic_reimbursement_adjustments,
    block_snap_ebt_tender_for_banned_item,
    coordinate_emergency_wic_substitute_approval,
    generate_wic_participant_shelf_talker,
    handle_infant_formula_wic_voucher_swap,
    log_declined_wic_benefit_attempts,
    notify_state_wic_agency_liaison,
    remove_recalled_upc_from_state_wic_apl,
    update_self_checkout_wic_validation_table,
    validate_cereal_size_ounce_substitute,
)


def test_wic_ebt_blocks():
    assert WicAplHotfixEngine().status == "ACTIVE"
    assert EbtEligibilityBlocker().status == "ACTIVE"
    assert remove_recalled_upc_from_state_wic_apl("CA", "012345678905")["removed"] is True
    assert coordinate_emergency_wic_substitute_approval("CA", "012345678912")["approved"] is True
    assert handle_infant_formula_wic_voucher_swap("V1", "INF2")["alt_formula_sku"] == "INF2"
    assert block_snap_ebt_tender_for_banned_item("S1")["ebt_blocked"] is True
    assert update_self_checkout_wic_validation_table("WM1", "v2")["apl_version"] == "v2"
    assert "WIC NOTICE" in generate_wic_participant_shelf_talker("Item A", "Item B")
    assert log_declined_wic_benefit_attempts("WM1", "U1")["upc"] == "U1"
    assert notify_state_wic_agency_liaison("CA", "REC1")["state"] == "CA"
    assert validate_cereal_size_ounce_substitute(18.0, 36.0)["eligible"] is True
    assert audit_wic_reimbursement_adjustments("CLM1", 22.50)["amount_usd"] == 22.50
