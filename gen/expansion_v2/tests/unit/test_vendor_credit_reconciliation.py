"""Unit tests for recallstorm.vendor.credit_reconciliation."""
from recallstorm.vendor.credit_reconciliation import (
    DeductionMatcher,
    VendorCreditLedger,
    audit_3pl_reclamation_settlement_files,
    calculate_cash_discount_reversal_impact,
    clear_aged_open_deduction_balances,
    close_financial_recall_event_ledger,
    escalate_insolvent_vendor_write_offs,
    generate_vendor_statement_of_account_pdf,
    match_vendor_credit_memo_to_rma_id,
    reconcile_unit_cost_discrepancies_on_credit,
    resolve_short_paid_invoice_disputes,
    track_swell_allowance_vs_recall_eligibility,
)


def test_credit_reconciliation():
    assert VendorCreditLedger().status == "ACTIVE"
    assert DeductionMatcher().status == "ACTIVE"
    assert match_vendor_credit_memo_to_rma_id("CM1", "RMA1", 1000.0, 900.0)["shortfall_usd"] == 100.0
    assert reconcile_unit_cost_discrepancies_on_credit(2.50, 2.00, 100) == 50.0
    assert track_swell_allowance_vs_recall_eligibility(True)["billable_above_swell"] is True
    assert clear_aged_open_deduction_balances(["D2", "D1"]) == ["D1", "D2"]
    assert audit_3pl_reclamation_settlement_files(500.0, 480.0)["variance_usd"] == 20.0
    assert calculate_cash_discount_reversal_impact(1000.0, 0.02) == 980.0
    assert resolve_short_paid_invoice_disputes("DSP1", 100.0)["rebilled_usd"] == 100.0
    assert generate_vendor_statement_of_account_pdf("V1", 2)["open_recalls"] == 2
    assert escalate_insolvent_vendor_write_offs("V1", 500.0)["write_off_usd"] == 500.0
    assert close_financial_recall_event_ledger("R1", 0.0)["closed"] is True
