"""Integration test 06: core -> gs1 -> store -> food_safety -> inventory."""
from recallstorm.core.ids import make_task_id
from recallstorm.food_safety.temperature_holds import evaluate_fda_tcs_four_hour_rule
from recallstorm.gs1.gtin import is_valid_gtin, normalize_gtin
from recallstorm.inventory.on_hand_reconciliation import compare_physical_pull_to_on_hand
from recallstorm.inventory.quarantine_bins import assign_locked_backroom_cage_bin
from recallstorm.store.backroom import stage_returns


def test_flow_food_safety_and_inventory():
    g14 = normalize_gtin("073621007017")
    assert is_valid_gtin(g14)
    tcs = evaluate_fda_tcs_four_hour_rule(260.0, 52.0)
    assert tcs["discard"] is True
    staged = stage_returns("WM1563", 4)
    assert staged["staged_cases"] == 4
    cage = assign_locked_backroom_cage_bin("WM1563", False)
    assert "QCAGE" in cage
    var = compare_physical_pull_to_on_hand(48, 50)
    assert var["variance"] == -2
    assert make_task_id("WM1563", "S1", "PULL", 1).startswith("TSK-")
