"""Unit tests for recallstorm.inventory.consignment_stock."""
from recallstorm.inventory.consignment_stock import (
    ConsignmentHoldTracker,
    ScanBasedTradingLedger,
    audit_unremoved_vendor_racks,
    block_sbt_daily_pos_settlement,
    exclude_consignment_from_shrink_gl,
    generate_consignment_removal_receipt,
    identify_sbt_vendor_owned_skus,
    notify_sbt_route_representative,
    reconcile_consignment_pad_counts,
    record_zero_cost_quarantine_units,
    validate_sbt_contract_recall_terms,
    verify_dsd_driver_buyback_scan,
)


def test_consignment_stock():
    assert ScanBasedTradingLedger().status == "ACTIVE"
    assert ConsignmentHoldTracker().status == "ACTIVE"
    assert identify_sbt_vendor_owned_skus([{"sku_id": "S1", "is_sbt": True}]) == ["S1"]
    assert exclude_consignment_from_shrink_gl(500.0, 150.0) == 350.0
    assert notify_sbt_route_representative("V1", "WM1")["vendor_id"] == "V1"
    assert record_zero_cost_quarantine_units("WM1", "S1", 10)["book_cost_usd"] == 0.0
    assert verify_dsd_driver_buyback_scan("DRV1", 4)["cases"] == 4
    assert reconcile_consignment_pad_counts(10, 8) == -2
    assert block_sbt_daily_pos_settlement("S1")["settlement_frozen"] is True
    assert audit_unremoved_vendor_racks("WM1", 1)["associate_pull_triggered"] is True
    assert generate_consignment_removal_receipt("WM1", "V1", 10)["units"] == 10
    assert validate_sbt_contract_recall_terms("CNT1", True)["labor_reimbursable"] is True
