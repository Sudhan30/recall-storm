"""Edge case tests for recallstorm.scenario_gs1.scenario."""
from recallstorm.scenario_gs1.scenario import load_gs1_scenario, recall_skus


def test_scenario_gs1_edge():
    sc = load_gs1_scenario({})
    assert recall_skus(sc, []) == []
