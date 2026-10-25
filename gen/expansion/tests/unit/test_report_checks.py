"""Unit tests for recallstorm.report.checks."""
from contract import load_datapack
from recallstorm.ingest.manifest_io import sample_datapack
from recallstorm.plan.assemble import assemble_plan
from recallstorm.report.checks import (
    CheckReport,
    check_capacity,
    check_conservation,
    check_contradictions,
    check_deadline,
    check_labor,
    check_refs,
    checks_to_json,
    run_all_checks,
)


def test_all_invariant_checks():
    pack = sample_datapack(load_datapack("data"), max_stores=3, seed=42)
    scen = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    records = assemble_plan(pack, scen)
    assert check_refs(records) == []
    assert check_conservation(records, pack) == []
    assert check_capacity(records, pack) == []
    assert check_labor(records, pack) == []
    assert check_deadline(records, scen["deadline"]) == []
    assert check_contradictions(records) == []

    rep = run_all_checks(records, pack, scen["deadline"])
    assert isinstance(rep, CheckReport) and rep.passed is True
    assert '"passed": true' in checks_to_json(rep)
