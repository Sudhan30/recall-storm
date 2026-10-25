"""Unit tests for recallstorm.scenario_gs1.scenario."""
from contract import Sku
from recallstorm.scenario_gs1.scenario import (
    Gs1Scenario,
    gs1_scenario_summary,
    load_gs1_scenario,
    recall_from_openfda,
    recall_lots,
    recall_plan,
    recall_rule,
    recall_skus,
    recall_window,
)
from tests.unit.test_plan_assemble import _sample_pack


def test_scenario_gs1():
    rep = {
        "recall_number": "F-100-2026",
        "product_description": "Sprinkles UPC 07502264930572",
        "code_info": "Lot: L2601A",
        "reason_for_recall": "Contains Red 3",
        "distribution_pattern": "CA",
    }
    sc = recall_from_openfda(rep)
    assert isinstance(sc, Gs1Scenario)
    assert recall_lots(sc) == ["L2601A"]
    assert len(recall_window(sc)) == 2
    assert recall_rule(sc).rule_id == "GS1_F-100-2026"
    s1 = Sku("FDC1034191", "07502264930572", "Sprinkles", "B", "baking", "RED 3", True, False, 6, 2.0, 10.0)
    assert recall_skus(sc, [s1]) == [s1]
    assert gs1_scenario_summary(sc)["lot_count"] == 1
    assert load_gs1_scenario({"scenario_id": "s1", "lots": ["L1"]}).scenario_id == "s1"

    pack = _sample_pack()
    plan = recall_plan(sc, pack)
    assert len(plan) > 0
