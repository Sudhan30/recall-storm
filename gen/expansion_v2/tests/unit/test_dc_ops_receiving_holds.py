"""Unit tests for recallstorm.dc_ops.receiving_holds."""
from recallstorm.dc_ops.receiving_holds import (
    DockDoorQuarantine,
    InboundReceivingBlock,
    alert_dc_qa_inspector_to_receiving_dock,
    block_auto_putaway_to_reserve_racking,
    capture_inbound_bol_and_lumper_notes,
    flag_recalled_po_line_on_receiving_rf,
    generate_osd_over_short_damage_refusal,
    log_driver_detention_for_lot_sorting,
    print_immediate_red_quarantine_pallet_lpn,
    reject_affected_lot_at_inbound_scan,
    release_clean_lots_on_split_delivery,
    segregate_mixed_lot_vendor_ti_hi_pallets,
)


def test_receiving_holds():
    assert InboundReceivingBlock().status == "ACTIVE"
    assert DockDoorQuarantine().status == "ACTIVE"
    assert flag_recalled_po_line_on_receiving_rf("PO1", "S1")["flagged"] is True
    assert reject_affected_lot_at_inbound_scan("L2601", {"L2601"})["rejected"] is True
    assert print_immediate_red_quarantine_pallet_lpn("DC_NORTH", 1) == "DC-RED-DC_NORTH-0001"
    assert segregate_mixed_lot_vendor_ti_hi_pallets(40, 15)["clean_cases"] == 25
    assert block_auto_putaway_to_reserve_racking("LPN1")["putaway_blocked"] is True
    assert log_driver_detention_for_lot_sorting("TR1", 45.0)["minutes"] == 45.0
    assert capture_inbound_bol_and_lumper_notes("BOL1", "Sorted 2 pallets")["bol_id"] == "BOL1"
    assert alert_dc_qa_inspector_to_receiving_dock("DC1", 12)["door_no"] == 12
    assert generate_osd_over_short_damage_refusal("PO1", 15)["refused_cases"] == 15
    assert release_clean_lots_on_split_delivery("PO1", 25)["clean_cases"] == 25
