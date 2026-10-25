"""Unit tests for recallstorm.vendor.dsd_coordination."""
from recallstorm.vendor.dsd_coordination import (
    DsdRecallExecution,
    RouteDriverSignOff,
    audit_driver_pulled_case_counts_at_exit,
    close_dsd_route_reconciliation_loop,
    escalate_missed_dsd_pickup_sla_window,
    lock_dsd_item_in_receiving_handheld,
    notify_dsd_bottler_bakery_dispatcher,
    prevent_unauthorized_dsd_shelf_restock,
    reconcile_driver_handwritten_credit_slips,
    schedule_driver_in_store_credit_pickup,
    track_unserviced_rural_store_dsd_holds,
    verify_backdoor_dex_return_invoice_scan,
)


def test_dsd_coordination():
    assert DsdRecallExecution().status == "ACTIVE"
    assert RouteDriverSignOff().status == "ACTIVE"
    assert notify_dsd_bottler_bakery_dispatcher("FL1", ["SAMS4767"])["stores"] == ["SAMS4767"]
    assert schedule_driver_in_store_credit_pickup("SAMS4767", "FL1", 24)["window_hours"] == 24
    assert verify_backdoor_dex_return_invoice_scan("DEX1", 120.0)["credit_usd"] == 120.0
    assert audit_driver_pulled_case_counts_at_exit(10, 10)["matched"] is True
    assert prevent_unauthorized_dsd_shelf_restock("SAMS4767", "S1")["blocked"] is True
    assert lock_dsd_item_in_receiving_handheld("S1")["dex_blocked"] is True
    assert reconcile_driver_handwritten_credit_slips("SLP1", 10, 3.5) == 35.0
    assert track_unserviced_rural_store_dsd_holds(["WM1", "WM2"], {"WM1"}) == ["WM2"]
    assert escalate_missed_dsd_pickup_sla_window("WM2", 60.0, 48.0)["destroy_and_bill"] is True
    assert close_dsd_route_reconciliation_loop("SAMS4767", "DEX1")["closed"] is True
