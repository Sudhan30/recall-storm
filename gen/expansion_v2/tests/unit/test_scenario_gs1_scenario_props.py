"""Property tests for recallstorm.scenario_gs1.scenario."""
from recallstorm.scenario_gs1.scenario import load_gs1_scenario, recall_lots


def test_load_gs1_scenario_preserves_lots():
    lots = [f"LOT{i}" for i in range(10)]
    sc = load_gs1_scenario({"lots": lots})
    assert recall_lots(sc) == lots
