"""Unit tests for recallstorm.food_safety.pest_control_holds."""
from recallstorm.food_safety.pest_control_holds import (
    GnawDamageEvaluator,
    PestSightingQuarantine,
    audit_dock_door_brush_seals,
    authorize_sealed_can_salvage_wash,
    generate_pest_destruction_affidavit,
    link_sighting_to_3pl_trailer,
    log_rodent_evidence_location,
    map_adjacent_pallet_buffer_zone,
    quarantine_compromised_dry_goods,
    schedule_licensed_fumigation_visit,
    track_pheromone_trap_catch_counts,
    verify_uv_blacklight_urine_scan,
)


def test_pest_control_holds():
    assert PestSightingQuarantine().status == "ACTIVE"
    assert GnawDamageEvaluator().status == "ACTIVE"
    assert log_rodent_evidence_location("WM1", "A04-B2")["bay_code"] == "A04-B2"
    assert map_adjacent_pallet_buffer_zone(5, 1) == [4, 5, 6]
    assert verify_uv_blacklight_urine_scan("LPN1", True)["adulterated"] is True
    assert quarantine_compromised_dry_goods("WM1", ["S1"])["skus"] == ["S1"]
    assert schedule_licensed_fumigation_visit("WM1", 2)["urgency_hours"] == 2
    assert track_pheromone_trap_catch_counts("TRP1", 8, 5)["infestation_alert"] is True
    assert audit_dock_door_brush_seals("DC1", 0)["passed"] is True
    assert authorize_sealed_can_salvage_wash("S1", True)["eligible"] is True
    assert generate_pest_destruction_affidavit("WM1", 10)["cases_destroyed"] == 10
    assert link_sighting_to_3pl_trailer("TR1", "CAR1")["rejected"] is True
