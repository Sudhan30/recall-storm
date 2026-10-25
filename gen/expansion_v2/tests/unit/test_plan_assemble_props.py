"""Property tests for recallstorm.plan.assemble."""
from recallstorm.plan.assemble import assemble_plan, plan_hash, validate_plan_refs
from tests.unit.test_plan_assemble import _sample_pack


def test_assemble_plan_determinism_props():
    pack = _sample_pack()
    scenario = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    p1 = assemble_plan(pack, scenario)
    p2 = assemble_plan(pack, scenario)
    assert plan_hash(p1) == plan_hash(p2)
    assert validate_plan_refs(p1) == []
