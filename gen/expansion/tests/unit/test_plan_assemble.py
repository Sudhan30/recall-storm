"""Unit tests for recallstorm.plan.assemble."""
from datetime import datetime
from contract import load_datapack
from recallstorm.ingest.manifest_io import sample_datapack
from recallstorm.plan.assemble import (
    PlanAssembler,
    assemble_plan,
    merge_plans,
    plan_hash,
    plan_records,
    plan_stats,
    plan_to_jsonl,
    run_record,
    validate_plan_refs,
)


def test_assemble_plan_and_validate(tmp_path):
    pack = sample_datapack(load_datapack("data"), max_stores=3, seed=42)
    scen = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    pa = PlanAssembler("ca_red3", "CA", ("CA_AB418_RED3",), datetime.fromisoformat(scen["as_of"]), datetime.fromisoformat(scen["deadline"]))
    assert pa.scenario_id == "ca_red3"

    records = assemble_plan(pack, scen)
    assert validate_plan_refs(records) == []
    stats = plan_stats(records)
    assert stats["run"] == 1
    assert stats["store_playbook"] == 3
    assert plan_hash(records) == plan_hash(records)

    out_file = tmp_path / "plan.jsonl"
    assert plan_to_jsonl(records, out_file) == len(records)
    merged = merge_plans(records[:5], records[:5])
    assert len(merged) == 5
    r_rec = run_record("ca_red3", scen["as_of"], ["CA_AB418_RED3"])
    assert len(plan_records(r_rec, [], [], [], [], [], [], [], [])) == 1
