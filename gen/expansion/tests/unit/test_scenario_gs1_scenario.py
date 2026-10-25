"""Unit tests for recallstorm.scenario_gs1.scenario."""
from contract import load_datapack
from recallstorm.ingest.manifest_io import sample_datapack
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


def test_gs1_scenario_workflow():
    report = {
        "recall_number": "F-0100-2026",
        "product_description": "Rainbow Sprinkles UPC 07502264930572",
        "code_info": "Lot: L2601A, Batch B9920",
        "reason_for_recall": "Contains FD&C Red No. 3",
        "distribution_pattern": "CA",
    }
    scen = recall_from_openfda(report)
    assert isinstance(scen, Gs1Scenario)
    assert recall_lots(scen) == ["L2601A", "B9920"]
    s_dt, e_dt = recall_window(scen)
    assert s_dt < e_dt
    rule = recall_rule(scen)
    assert rule.rule_id == "OPENFDA_F-0100-2026"

    loaded = load_gs1_scenario(report)
    assert loaded == scen

    pack = sample_datapack(load_datapack("data"), max_stores=2, seed=42)
    matched = recall_skus(scen, pack.skus)
    assert any(s.sku_id == "FDC1034191" for s in matched)
    plan = recall_plan(scen, pack)
    assert len(plan) >= 2
    assert gs1_scenario_summary(scen)["gtin_count"] == 1
