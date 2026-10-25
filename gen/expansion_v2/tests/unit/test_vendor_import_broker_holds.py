"""Unit tests for recallstorm.vendor.import_broker_holds."""
from recallstorm.vendor.import_broker_holds import (
    CustomsEntryQuarantine,
    ImportHoldCoordinator,
    audit_foreign_supplier_fsvp_dossiers,
    calculate_port_demurrage_detention_fees,
    coordinate_fda_private_lab_sampling_packet,
    hold_deconsolidated_transload_pallets,
    manage_export_or_destruction_under_customs,
    match_fda_predict_import_hold_notice,
    release_may_proceed_entries_to_dc,
    track_notice_of_fda_action_detention,
    trace_ocean_container_bol_to_drayage,
    verify_customs_bond_redelivery_demand,
)


def test_import_broker_holds():
    assert ImportHoldCoordinator().status == "ACTIVE"
    assert CustomsEntryQuarantine().status == "ACTIVE"
    assert match_fda_predict_import_hold_notice("ENT1", 1)["entry_no"] == "ENT1"
    assert trace_ocean_container_bol_to_drayage("MSCU123", "DC_SOUTH")["dc_id"] == "DC_SOUTH"
    assert verify_customs_bond_redelivery_demand("4647-1", 50000.0)["bond_amount_usd"] == 50000.0
    assert coordinate_fda_private_lab_sampling_packet("ENT1", "LAB1")["lab_id"] == "LAB1"
    assert hold_deconsolidated_transload_pallets("MSCU123", ["LPN1"])["lpns"] == ["LPN1"]
    assert track_notice_of_fda_action_detention("ENT1", "DETAINED")["status"] == "DETAINED"
    assert calculate_port_demurrage_detention_fees(10, 225.0) == 2250.0
    assert manage_export_or_destruction_under_customs("ENT1", "DESTROY_CBP")["mode"] == "DESTROY_CBP"
    assert audit_foreign_supplier_fsvp_dossiers("FSUP1", True)["compliant"] is True
    assert release_may_proceed_entries_to_dc("ENT1", True)["released"] is True
