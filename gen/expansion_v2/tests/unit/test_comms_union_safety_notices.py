"""Unit tests for recallstorm.comms.union_safety_notices."""
from recallstorm.comms.union_safety_notices import (
    HazmatHandlingNotice,
    LaborUnionSafetyBrief,
    address_immunocompromised_staff_opt_out,
    archive_union_grievance_communications,
    communicate_mandatory_overtime_rules,
    distribute_sds_safety_data_sheets,
    document_joint_safety_committee_review,
    log_associate_chemical_exposure_incident,
    notify_ufcw_steward_of_hazmat_recall,
    provide_ergonomic_heavy_lifting_guide,
    specify_caustic_leaking_product_ppe,
    verify_spill_kit_availability_in_aisles,
)


def test_union_safety_notices():
    assert LaborUnionSafetyBrief().status == "ACTIVE"
    assert HazmatHandlingNotice().status == "ACTIVE"
    assert notify_ufcw_steward_of_hazmat_recall("UFCW-770", "S1")["chapter"] == "UFCW-770"
    assert "CHEMICAL_GOGGLES" in specify_caustic_leaking_product_ppe(13.0)
    assert communicate_mandatory_overtime_rules(["A1", "A2"], 1) == ["A1"]
    assert log_associate_chemical_exposure_incident("A1", "S1")["associate_id"] == "A1"
    assert provide_ergonomic_heavy_lifting_guide(65.0)["team_lift_required"] is True
    assert verify_spill_kit_availability_in_aisles("WM1", 2)["ready"] is True
    assert address_immunocompromised_staff_opt_out("A1", True)["reassigned"] is True
    assert document_joint_safety_committee_review("COM1", True)["approved"] is True
    assert distribute_sds_safety_data_sheets("S1", "https://sds.example/1")["sku_id"] == "S1"
    assert archive_union_grievance_communications("GRV1", True)["resolved"] is True
