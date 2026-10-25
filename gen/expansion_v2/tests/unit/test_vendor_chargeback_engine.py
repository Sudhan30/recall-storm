"""Unit tests for recallstorm.vendor.chargeback_engine."""
from recallstorm.vendor.chargeback_engine import (
    FeeScheduleCalculator,
    RecallChargebackInvoice,
    apply_per_unit_handling_and_hauling_rate,
    attach_store_scan_audit_backup_csv,
    bill_pos_programming_and_signage_flat_fee,
    calculate_per_store_execution_labor_fee,
    compute_lost_gross_margin_recovery,
    deduct_chargeback_from_ap_remittance,
    enforce_master_vendor_agreement_caps,
    escalate_unpaid_private_label_claims,
    export_erp_accounts_receivable_debit,
    handle_vendor_chargeback_dispute_claim,
)


def test_chargeback_engine():
    assert RecallChargebackInvoice().status == "ACTIVE"
    assert FeeScheduleCalculator().status == "ACTIVE"
    assert calculate_per_store_execution_labor_fee(20, 75.0) == 1500.0
    assert apply_per_unit_handling_and_hauling_rate(100, 0.50) == 50.0
    assert bill_pos_programming_and_signage_flat_fee("Class I") == 5000.0
    assert compute_lost_gross_margin_recovery(100, 4.0, 2.5) == 150.0
    assert attach_store_scan_audit_backup_csv("INV1", 20)["scan_rows"] == 20
    assert deduct_chargeback_from_ap_remittance(10000.0, 4000.0)["deducted_usd"] == 4000.0
    assert handle_vendor_chargeback_dispute_claim("DSP1", False)["upheld"] is True
    assert enforce_master_vendor_agreement_caps(150000.0, 100000.0) == 100000.0
    assert escalate_unpaid_private_label_claims("V1", 75)["escalate"] is True
    assert export_erp_accounts_receivable_debit("INV1", 6700.0)["total_usd"] == 6700.0
