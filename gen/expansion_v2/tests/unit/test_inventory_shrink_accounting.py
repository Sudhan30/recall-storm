"""Unit tests for recallstorm.inventory.shrink_accounting."""
from recallstorm.inventory.shrink_accounting import (
    FinancialWriteOffEngine,
    RecallShrinkJournal,
    allocate_destruction_hauling_fees,
    audit_high_value_shrink_approvals,
    calculate_landed_cost_extended_value,
    classify_vendor_funded_vs_retail_loss,
    export_period_end_recall_accrual,
    generate_tax_deduction_destruction_cert,
    post_general_ledger_shrink_entries,
    reconcile_swell_allowance_offsets,
    track_insurance_deductible_accumulation,
    value_in_store_production_wip_loss,
)


def test_shrink_accounting():
    assert RecallShrinkJournal().status == "ACTIVE"
    assert FinancialWriteOffEngine().status == "ACTIVE"
    assert classify_vendor_funded_vs_retail_loss("FDA additive ban") == "VENDOR_FUNDED"
    assert calculate_landed_cost_extended_value(100, 2.0, 0.05) == 210.0
    assert post_general_ledger_shrink_entries("GL-5010", 210.0)["amount_usd"] == 210.0
    fees = allocate_destruction_hauling_fees(100.0, {"WM1": 1, "WM2": 3})
    assert fees == {"WM1": 25.0, "WM2": 75.0}
    assert value_in_store_production_wip_loss(50.0, 25.0) == 75.0
    assert track_insurance_deductible_accumulation(300000.0, 250000.0)["claimable_usd"] == 50000.0
    assert reconcile_swell_allowance_offsets(500.0, 50.0) == 500.0
    assert generate_tax_deduction_destruction_cert("RUN1", 500.0)["write_off_usd"] == 500.0
    assert audit_high_value_shrink_approvals(100000.0, True)["compliant"] is True
    assert export_period_end_recall_accrual("2026-Q4", 15000.0)["accrual_usd"] == 15000.0
