"""Unit tests for recallstorm.states.il_food_safety_act."""
from recallstorm.states.il_food_safety_act import (
    IlAdditiveBanRule,
    IlGracePeriodTracker,
    assess_il_distributor_liability,
    build_il_shelf_pull_order,
    calculate_il_sell_through_days,
    check_il_sb2637_scope,
    evaluate_il_bakery_exemption,
    filter_il_jurisdiction_stores,
    format_il_inspection_sheet,
    parse_il_idph_guidance,
    track_il_phase_out_schedule,
    verify_il_reformulated_lot,
)


def test_il_food_safety_act():
    assert IlAdditiveBanRule().status == "ACTIVE"
    assert IlGracePeriodTracker().status == "ACTIVE"
    assert check_il_sb2637_scope("RED3", True)["in_scope"] is True
    assert evaluate_il_bakery_exemption("WM1")["exempt"] is False
    assert calculate_il_sell_through_days(30) == 30
    assert filter_il_jurisdiction_stores([{"store_id": "WM1", "state": "IL"}, {"store_id": "WM2", "state": "CA"}]) == ["WM1"]
    assert parse_il_idph_guidance("IDPH SB 2637 guidance")["effective_year"] == 2028
    assert build_il_shelf_pull_order("WM1", "S1", 12)["units"] == 12
    assert verify_il_reformulated_lot("CLN2027", "CLN")["clean"] is True
    assert assess_il_distributor_liability(4, 250.0) == 1000.0
    assert format_il_inspection_sheet("WM1", 10)["checked_skus"] == 10
    assert track_il_phase_out_schedule("M1", 80.0)["pct_complete"] == 80.0
