"""Unit tests for recallstorm.pricing.refund_policies."""
from recallstorm.pricing.refund_policies import (
    NoReceiptReturnEngine,
    RecallRefundPolicy,
    bypass_return_window_day_limits,
    calculate_state_bottle_deposit_refund,
    enable_no_receipt_full_retail_refund,
    flag_serial_return_fraud_velocity,
    generate_customer_refund_receipt_disclaimer,
    issue_extra_goodwill_loyalty_points,
    link_refund_scan_to_quarantine_bin,
    prevent_returned_item_restock_to_shelf,
    process_opened_consumed_package_return,
    reconcile_recall_refund_tender_totals,
)


def test_refund_policies():
    assert RecallRefundPolicy().status == "ACTIVE"
    assert NoReceiptReturnEngine().status == "ACTIVE"
    assert enable_no_receipt_full_retail_refund("S1", 4.99)["refund_usd"] == 4.99
    assert bypass_return_window_day_limits(180)["accepted"] is True
    assert calculate_state_bottle_deposit_refund(12, 0.05) == 0.60
    assert issue_extra_goodwill_loyalty_points("L1", 500)["points"] == 500
    assert process_opened_consumed_package_return("S1", 10.0)["full_refund"] is True
    assert link_refund_scan_to_quarantine_bin("TX1")["quarantine_bin"] == "CS-QBIN-01"
    assert prevent_returned_item_restock_to_shelf("S1")["restock_blocked"] is True
    assert flag_serial_return_fraud_velocity("C1", 15, 10)["flagged"] is True
    assert "REC1" in generate_customer_refund_receipt_disclaimer("REC1")
    assert reconcile_recall_refund_tender_totals([4.99, 5.01]) == 10.0
