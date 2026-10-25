"""Unit tests for recallstorm.recall_lots.consignee_reconciliation."""
from recallstorm.recall_lots.consignee_reconciliation import (
    ConsigneeShipmentLedger,
    ShipToMatcher,
    audit_unmatched_po_receipts,
    calculate_net_shipped_exposure,
    flag_diverted_wholesaler_loads,
    generate_consignee_variance_table,
    identify_drop_ship_store_deliveries,
    match_asn_bol_to_recall_lots,
    reconcile_billed_vs_received_cases,
    resolve_dc_cross_dock_splits,
    track_in_transit_carrier_trailers,
    verify_zero_shipment_attestation,
)


def test_consignee_reconciliation():
    assert ConsigneeShipmentLedger().status == "ACTIVE"
    assert ShipToMatcher().status == "ACTIVE"
    assert match_asn_bol_to_recall_lots(["L1", "L2"], {"L2"}) == ["L2"]
    assert reconcile_billed_vs_received_cases(10, 8)["variance"] == -2
    assert identify_drop_ship_store_deliveries([{"store_id": "WM1", "drop_ship": True}]) == ["WM1"]
    assert flag_diverted_wholesaler_loads("BOL1", False)["flagged"] is True
    assert calculate_net_shipped_exposure(50, 30) == 20
    assert resolve_dc_cross_dock_splits("LPN1", {"WM1": 5, "WM2": 5})["total_cases"] == 10
    assert audit_unmatched_po_receipts(["PO2", "PO1"]) == ["PO1", "PO2"]
    assert track_in_transit_carrier_trailers("TR1", "2026-12-31")["trailer_id"] == "TR1"
    assert generate_consignee_variance_table([{"a": 1}])["row_count"] == 1
    assert verify_zero_shipment_attestation("WM1", 0)["zero_confirmed"] is True
