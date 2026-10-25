"""Unit tests for recallstorm.food_safety.produce_wash_logs."""
from recallstorm.food_safety.produce_wash_logs import (
    AntimicrobialWashMonitor,
    ProduceCrispingRecord,
    audit_single_pass_rinse_flow,
    calculate_cut_produce_display_hours,
    flag_cut_fruit_immersion_timeout,
    generate_fresh_cut_pull_sheet,
    link_cut_room_batch_to_trays,
    log_wash_tank_water_temp_diff,
    track_leafy_green_lot_commingling,
    trigger_wash_solution_dump_alert,
    validate_test_strip_lot_expiry,
    verify_peracetic_acid_ppm_range,
)


def test_produce_wash_logs():
    assert ProduceCrispingRecord().status == "ACTIVE"
    assert AntimicrobialWashMonitor().status == "ACTIVE"
    assert verify_peracetic_acid_ppm_range(60.0)["compliant"] is True
    assert log_wash_tank_water_temp_diff(55.0, 50.0)["safe"] is True
    assert flag_cut_fruit_immersion_timeout(8.0, 5.0)["timeout"] is True
    assert track_leafy_green_lot_commingling("SINK1", ["L1", "L2"])["commingled"] is True
    assert validate_test_strip_lot_expiry("ST1", "2027-01-01")["valid"] is True
    assert audit_single_pass_rinse_flow("WM1", True)["compliant"] is True
    assert link_cut_room_batch_to_trays("B1", 20)["tray_count"] == 20
    assert trigger_wash_solution_dump_alert(75.0, 50.0)["dump_required"] is True
    assert calculate_cut_produce_display_hours(5.0, 4.0)["expired"] is True
    assert generate_fresh_cut_pull_sheet("WM1", ["B1"])["batches"] == ["B1"]
