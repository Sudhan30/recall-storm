"""Unit tests for recallstorm.food_safety.allergen_cross_contact."""
from recallstorm.food_safety.allergen_cross_contact import (
    AllergenMatrix,
    LineChangeoverValidator,
    audit_in_store_repack_labels,
    build_allergen_sanitation_task,
    check_deli_slicer_cleaning_gap,
    detect_shared_fryer_exposure,
    evaluate_bakery_rack_drip_risk,
    flag_bulk_bin_scoop_migration,
    score_cross_contact_severity,
    trace_sesame_flour_dust_zones,
    validate_may_contain_advisory_override,
    verify_allergen_segregation_planogram,
)


def test_allergen_cross_contact():
    assert AllergenMatrix().status == "ACTIVE"
    assert LineChangeoverValidator().status == "ACTIVE"
    assert detect_shared_fryer_exposure("FRY1", ["FISH", "WHEAT"])["cross_contact"] is True
    assert evaluate_bakery_rack_drip_risk("PEANUT", "Plain Bread")["high_risk"] is True
    assert check_deli_slicer_cleaning_gap(5.0, 4.0)["overdue"] is True
    assert flag_bulk_bin_scoop_migration("BIN1", False)["flagged"] is True
    assert verify_allergen_segregation_planogram("A01", True)["compliant"] is True
    assert audit_in_store_repack_labels("S1", ["MILK"])["declared"] == ["MILK"]
    assert "SESAME" in trace_sesame_flour_dust_zones("BENCH1")["allergens"]
    assert build_allergen_sanitation_task("WM1", "DELI")["dept"] == "DELI"
    assert validate_may_contain_advisory_override(True)["allowed"] is True
    assert score_cross_contact_severity("PEANUT", True) == 9
