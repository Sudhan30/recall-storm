"""Unit tests for recallstorm.pricing.bottle_deposit_credits."""
from recallstorm.pricing.bottle_deposit_credits import (
    ContainerDepositReconciler,
    CrvRedemptionBlocker,
    adjust_crushed_beverage_can_counts,
    audit_bottle_room_quarantine_bags,
    block_reverse_vending_machine_barcodes,
    calculate_unredeemed_crv_tax_credit,
    credit_customer_deposit_on_recall_return,
    export_state_beverage_container_report,
    generate_calrecycle_destruction_notice,
    handle_multi_state_deposit_rate_diffs,
    reconcile_distributor_deposit_chargebacks,
    waive_handling_fee_on_recalled_flats,
)


def test_bottle_deposit_credits():
    assert ContainerDepositReconciler().status == "ACTIVE"
    assert CrvRedemptionBlocker().status == "ACTIVE"
    assert calculate_unredeemed_crv_tax_credit(100, 0.05) == 5.0
    assert block_reverse_vending_machine_barcodes("WM1", "012345678905")["rvm_updated"] is True
    assert reconcile_distributor_deposit_chargebacks(10, 24, 0.05) == 12.0
    assert adjust_crushed_beverage_can_counts(10.0, 32.0) == 320
    assert handle_multi_state_deposit_rate_diffs("CA", 12.0) == 0.05
    assert handle_multi_state_deposit_rate_diffs("CA", 32.0) == 0.10
    assert generate_calrecycle_destruction_notice("RUN1", 240)["containers"] == 240
    assert audit_bottle_room_quarantine_bags("WM1", 2)["bags"] == 2
    assert credit_customer_deposit_on_recall_return(4.99, 0.60) == 5.59
    assert waive_handling_fee_on_recalled_flats(5)["waived"] is True
    assert export_state_beverage_container_report("CA", 12.0)["total_crv_usd"] == 12.0
