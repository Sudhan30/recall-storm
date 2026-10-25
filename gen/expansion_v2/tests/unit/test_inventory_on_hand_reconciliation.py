"""Unit tests for recallstorm.inventory.on_hand_reconciliation."""
from recallstorm.inventory.on_hand_reconciliation import (
    PerpetualInventoryLedger,
    RecallVarianceReconciler,
    account_for_unscanned_pos_cart_items,
    adjust_phantom_inventory_balances,
    calculate_unexplained_lot_discrepancy,
    compare_physical_pull_to_on_hand,
    flag_negative_on_hand_anomalies,
    lock_sku_from_auto_replenishment,
    post_erp_inventory_adjustment_journal,
    reconcile_click_and_collect_stagings,
    resolve_in_transit_asn_quantities,
    snapshot_pre_recall_book_inventory,
)


def test_on_hand_reconciliation():
    assert PerpetualInventoryLedger().status == "ACTIVE"
    assert RecallVarianceReconciler().status == "ACTIVE"
    assert snapshot_pre_recall_book_inventory("WM1", {"S1": 10, "S2": 5})["total_units"] == 15
    assert compare_physical_pull_to_on_hand(8, 10)["variance"] == -2
    assert resolve_in_transit_asn_quantities(10, 12) == 22
    assert adjust_phantom_inventory_balances("WM1", "S1", 0)["new_balance"] == 0
    assert account_for_unscanned_pos_cart_items(10, 2) == 12
    assert reconcile_click_and_collect_stagings(10, 3) == 13
    assert flag_negative_on_hand_anomalies({"S1": -2, "S2": 5}) == ["S1"]
    assert calculate_unexplained_lot_discrepancy(100, 70, 25) == 5
    assert post_erp_inventory_adjustment_journal("WM1", "S1", -10)["delta_units"] == -10
    assert lock_sku_from_auto_replenishment("S1")["auto_order_locked"] is True
