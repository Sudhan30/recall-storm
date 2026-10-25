"""Unit tests for recallstorm.vendor.reformulation_tracker."""
from recallstorm.vendor.reformulation_tracker import (
    AdditivePhaseOutPlan,
    ReformulationMilestone,
    compare_old_vs_new_ingredient_decks,
    flag_delayed_vendor_r_and_d_milestones,
    ingest_updated_supplier_spec_sheets,
    manage_packaging_artwork_proof_signoff,
    monitor_clean_lot_first_ship_date,
    prevent_old_formulation_po_reordering,
    report_category_compliance_readiness_pct,
    track_bromate_red3_replacement_timeline,
    validate_transition_lot_cutover_code,
    verify_new_upc_gtin_assignment_rules,
)


def test_reformulation_tracker():
    assert ReformulationMilestone().status == "ACTIVE"
    assert AdditivePhaseOutPlan().status == "ACTIVE"
    assert track_bromate_red3_replacement_timeline("S1", "2026-09-01", "2027-01-01")["on_track"] is True
    assert ingest_updated_supplier_spec_sheets("S1", "SUGAR, BEET JUICE")["sku_id"] == "S1"
    assert compare_old_vs_new_ingredient_decks("SUGAR, RED 3", "SUGAR, BEET JUICE", "RED 3")["removed"] is True
    assert verify_new_upc_gtin_assignment_rules("001", "002")["distinct_gtin"] is True
    assert manage_packaging_artwork_proof_signoff("S1", True)["approved"] is True
    assert monitor_clean_lot_first_ship_date("S1", "L2610", "2026-10-01")["first_clean_lot"] == "L2610"
    assert prevent_old_formulation_po_reordering("S1")["po_blocked"] is True
    assert validate_transition_lot_cutover_code("L2615", "L2610") is True
    assert flag_delayed_vendor_r_and_d_milestones([{"sku_id": "S1", "ready_date": "2026-12-15"}], "2026-10-01") == ["S1"]
    assert report_category_compliance_readiness_pct(18, 20) == 90.0
