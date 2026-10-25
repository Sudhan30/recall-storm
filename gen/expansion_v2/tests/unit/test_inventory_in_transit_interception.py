"""Unit tests for recallstorm.inventory.in_transit_interception."""
from recallstorm.inventory.in_transit_interception import (
    ASNInterceptor,
    InTransitShipmentHold,
    alert_store_receiving_dock_handhelds,
    divert_en_route_dc_trailers,
    flag_inbound_dsd_delivery_manifests,
    generate_refusal_at_dock_instruction,
    notify_carrier_dispatcher_of_hold,
    reconcile_short_ship_from_intercept,
    scan_open_purchase_orders_for_lot,
    track_refused_freight_return_bol,
    update_expected_receipt_ledger,
    verify_seal_intact_on_refusal,
)


def test_in_transit_interception():
    assert InTransitShipmentHold().status == "ACTIVE"
    assert ASNInterceptor().status == "ACTIVE"
    assert scan_open_purchase_orders_for_lot([{"po_id": "PO1", "lots": ["L1"]}], "L1") == ["PO1"]
    assert flag_inbound_dsd_delivery_manifests("M1", ["S1"])["blocked_skus"] == ["S1"]
    assert alert_store_receiving_dock_handhelds("WM1", "BOL1")["bol_id"] == "BOL1"
    assert divert_en_route_dc_trailers("TR1", "DC_SOUTH")["diverted_to"] == "DC_SOUTH"
    assert generate_refusal_at_dock_instruction("BOL1", "S1")["action"] == "REFUSE_DELIVERY"
    assert track_refused_freight_return_bol("BOL1", "RBOL1")["return_bol"] == "RBOL1"
    assert update_expected_receipt_ledger("WM1", 5)["refused_cases"] == 5
    assert notify_carrier_dispatcher_of_hold("C1", "TR1")["carrier_id"] == "C1"
    assert verify_seal_intact_on_refusal("TR1", "S99", True)["intact"] is True
    assert reconcile_short_ship_from_intercept(20, 5) == 15
