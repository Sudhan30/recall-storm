"""Unit tests for recallstorm.report.checks."""
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
from tests.unit.test_plan_assemble import _sample_pack


def test_report_checks_pass_on_assembled_plan():
    pack = _sample_pack()
    sc = {
        "scenario_id": "ca_red3",
        "state": "CA",
        "rule_ids": ["CA_AB418_RED3"],
        "as_of": "2026-12-30T18:00:00-08:00",
        "deadline": "2027-01-01T00:00:00-08:00",
    }
    recs = assemble_plan(pack, sc)
    assert check_refs(recs) == []
    assert check_conservation(recs, pack.dc_stock) == []
    assert check_capacity(recs) == []
    assert check_labor(recs, pack.associates) == []
    assert check_deadline(recs, sc["deadline"]) == []
    assert check_contradictions(recs) == []

    rep = run_all_checks(recs, pack, sc["deadline"])
    assert isinstance(rep, CheckReport) and rep.passed is True
    assert '"passed": true' in checks_to_json(rep)
