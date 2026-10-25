"""Unit tests for recallstorm.dc_ops.carrier_tendering."""
from recallstorm.dc_ops.carrier_tendering import (
    HazmatCarrierSelector,
    ReverseLoadTendering,
    audit_reverse_freight_accessorial_bills,
    build_consolidated_recall_return_load,
    enforce_sealed_exclusive_use_trailer_rule,
    handle_carrier_turndown_waterfall_logic,
    monitor_in_transit_gps_breadcrumb_ping,
    negotiate_spot_market_backhaul_rates,
    tender_dedicated_truckload_via_edi_204,
    track_edi_990_load_acceptance_sla,
    validate_proof_of_delivery_at_reclamation,
    verify_carrier_hazmat_rcra_endorsements,
)


def test_carrier_tendering():
    assert ReverseLoadTendering().status == "ACTIVE"
    assert HazmatCarrierSelector().status == "ACTIVE"
    assert build_consolidated_recall_return_load("DC1", 20, 30000.0)["pallets"] == 20
    assert tender_dedicated_truckload_via_edi_204("LD1", "jbht")["scac"] == "JBHT"
    assert verify_carrier_hazmat_rcra_endorsements("CLNH", True)["approved"] is True
    assert track_edi_990_load_acceptance_sla(30.0, 60.0)["within_sla"] is True
    assert negotiate_spot_market_backhaul_rates(100.0, 2.85) == 285.0
    assert enforce_sealed_exclusive_use_trailer_rule("LD1", False)["exclusive_use"] is True
    assert monitor_in_transit_gps_breadcrumb_ping("LD1", 34.0, -118.0)["load_id"] == "LD1"
    assert handle_carrier_turndown_waterfall_logic(["SCAC1", "SCAC2"], "SCAC1") == "SCAC2"
    assert validate_proof_of_delivery_at_reclamation("LD1", True)["delivered"] is True
    assert audit_reverse_freight_accessorial_bills(500.0, 120.0) == 620.0
