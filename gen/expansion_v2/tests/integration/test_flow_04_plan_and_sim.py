"""Integration test 04: core -> rules -> allocate -> plan -> sim."""
from datetime import datetime
from recallstorm.core.jsonl import validate_record
from recallstorm.plan.assemble import assemble_plan, validate_plan_refs
from recallstorm.sim.metrics import completion_curve, late_tasks
from recallstorm.sim.replay import simulate_plan
from tests.unit.test_plan_assemble import _sample_pack


def test_flow_plan_and_sim():
    pack = _sample_pack()
    sc = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    plan_recs = assemble_plan(pack, sc)
    assert validate_plan_refs(plan_recs) == []
    for r in plan_recs:
        assert validate_record(r) == []

    dl = datetime.fromisoformat(sc["deadline"])
    events = simulate_plan(plan_recs, deadline=dl)
    assert len(events) > 0
    assert late_tasks(events, sc["deadline"]) == []
    assert len(completion_curve(events)) > 0
