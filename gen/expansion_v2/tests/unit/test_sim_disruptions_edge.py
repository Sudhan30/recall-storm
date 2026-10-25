"""Edge case tests for recallstorm.sim.disruptions."""
from recallstorm.sim.disruptions import disruption_report, seed_disruptions


def test_sim_disruptions_edge():
    assert seed_disruptions([]) == []
    assert disruption_report([])["count"] == 0
