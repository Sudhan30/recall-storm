"""Unit tests for recallstorm.food_safety.foreign_material."""
from recallstorm.food_safety.foreign_material import (
    ForeignMaterialIncident,
    XrayInspectionAudit,
    build_supplier_foreign_object_claim,
    calculate_complaint_per_million_units,
    check_fda_hard_sharp_7mm_rule,
    classify_fragment_material_type,
    evaluate_glass_brittle_plastic_breakage,
    generate_sensory_inspection_protocol,
    isolate_upstream_dumper_lots,
    match_sieve_screen_mesh_failure,
    trace_broken_belt_maintenance_log,
    verify_magnet_pull_test_records,
)


def test_foreign_material():
    assert ForeignMaterialIncident().status == "ACTIVE"
    assert XrayInspectionAudit().status == "ACTIVE"
    assert classify_fragment_material_type("Stainless steel wire") == "METAL"
    assert check_fda_hard_sharp_7mm_rule(9.5, False)["adulterated"] is True
    assert trace_broken_belt_maintenance_log("CONV1", 2)["hold_required"] is True
    assert match_sieve_screen_mesh_failure("SV1", True)["compromised"] is True
    assert evaluate_glass_brittle_plastic_breakage("Z1", 15.0)["sweep_radius_ft"] == 15.0
    assert isolate_upstream_dumper_lots("T1", ["L1"])["lots"] == ["L1"]
    assert verify_magnet_pull_test_records("M1", 20.0)["passed"] is True
    assert calculate_complaint_per_million_units(5, 1_000_000) == 5.0
    assert build_supplier_foreign_object_claim("V1", "INC1")["vendor_id"] == "V1"
    assert generate_sensory_inspection_protocol("S1", 10)["sample_cases"] == 10
