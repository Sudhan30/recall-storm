"""Unit tests for recallstorm.dc_ops.automation_inhibits."""
from recallstorm.dc_ops.automation_inhibits import (
    AsrsCraneLockout,
    SymboticBotQuarantine,
    audit_automated_storage_quarantine_inventory,
    divert_recalled_tote_on_high_speed_sorter,
    inhibit_depalletizer_robot_layer_pick,
    isolate_faulted_broken_case_in_shuttle_aisle,
    lock_autostore_or_symbotic_storage_bins,
    prevent_agv_forklift_autonomous_putaway,
    purge_unit_sorter_chute_accumulations,
    restore_mechatronics_cell_to_production,
    schedule_maintenance_retrieval_of_locked_tote,
    sync_wcs_warehouse_control_with_wms_hold,
)


def test_automation_inhibits():
    assert AsrsCraneLockout().status == "ACTIVE"
    assert SymboticBotQuarantine().status == "ACTIVE"
    assert lock_autostore_or_symbotic_storage_bins("CELL1", ["B1", "B2"])["locked"] is True
    assert inhibit_depalletizer_robot_layer_pick("ROB1", "S1")["inhibited"] is True
    assert divert_recalled_tote_on_high_speed_sorter("TOTE1")["diverted_to"] == "JACKPOT-QA-01"
    assert purge_unit_sorter_chute_accumulations("CH1", 8)["units"] == 8
    assert prevent_agv_forklift_autonomous_putaway("AGV1", "LPN1")["cancelled"] is True
    assert isolate_faulted_broken_case_in_shuttle_aisle("A1", 4)["isolated"] is True
    assert sync_wcs_warehouse_control_with_wms_hold({"L1"}, {"L1"})["in_sync"] is True
    assert schedule_maintenance_retrieval_of_locked_tote("TOTE1")["station"] == "DECANT-QA"
    assert audit_automated_storage_quarantine_inventory("CELL1", 40)["held_cases"] == 40
    assert restore_mechatronics_cell_to_production("CELL1", True)["online"] is True
