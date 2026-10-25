"""Unit tests for recallstorm.inventory.reverse_logistics_acct."""
from recallstorm.inventory.reverse_logistics_acct import (
    ReturnMerchandiseAuth,
    ReverseFreightLedger,
    age_unsettled_return_receivables,
    audit_hazmat_disposal_surcharges,
    calculate_restocking_fee_exemptions,
    close_completed_reverse_loop,
    generate_vendor_rma_reference_id,
    match_bill_of_lading_to_rma,
    post_pending_vendor_credit_memo,
    reconcile_crushed_bale_weights,
    track_3pl_reclamation_center_scans,
    value_return_center_staging_stock,
)


def test_reverse_logistics_acct():
    assert ReturnMerchandiseAuth().status == "ACTIVE"
    assert ReverseFreightLedger().status == "ACTIVE"
    rma = generate_vendor_rma_reference_id("V1", "REC1")
    assert rma == "RMA-V1-REC1"
    assert match_bill_of_lading_to_rma("BOL1", rma)["rma_id"] == rma
    assert value_return_center_staging_stock(10, 25.0) == 250.0
    assert track_3pl_reclamation_center_scans("RC1", 50)["scanned_cases"] == 50
    assert reconcile_crushed_bale_weights(1000.0, 980.0, 0.05)["within_tolerance"] is True
    assert audit_hazmat_disposal_surcharges(2, 185.0) == 370.0
    assert calculate_restocking_fee_exemptions(True) == 0.0
    assert post_pending_vendor_credit_memo(rma, 250.0)["amount_usd"] == 250.0
    assert age_unsettled_return_receivables(45) == "31_60"
    assert close_completed_reverse_loop(rma, True)["closed"] is True
