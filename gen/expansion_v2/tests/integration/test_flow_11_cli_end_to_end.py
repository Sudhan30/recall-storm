"""Integration test 11: End-to-end CLI run across core, rules, allocate, route, plan, sim, report, and cli."""
from datetime import datetime
from contract import PLAN_TYPES, Truck
from recallstorm.cli.main import main
from recallstorm.core.jsonl import read_jsonl
from recallstorm.report.checks import run_all_checks
from tests.unit.test_plan_assemble import _sample_pack


def test_flow_cli_end_to_end(tmp_path, monkeypatch):
    pack = _sample_pack()
    pack.trucks.append(Truck("DC_CENTRAL-T0", "DC_CENTRAL", 3400.0, 40000.0, datetime.fromisoformat("2026-12-31T08:00:00-08:00")))
    monkeypatch.setattr("recallstorm.cli.main.load_datapack_extended", lambda d: pack)

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "scenario_ca_red3.json").write_text(
        '{"scenario_id": "ca_red3", "state": "CA", "rule_ids": ["CA_AB418_RED3"], "as_of": "2026-12-30T18:00:00-08:00", "deadline": "2027-01-01T00:00:00-08:00"}',
        encoding="utf-8",
    )
    out_dir = tmp_path / "out_ca_red3"

    rc = main(["run", "--scenario", "ca_red3", "--data", str(data_dir), "--out", str(out_dir)])
    assert rc == 0

    plan_recs = read_jsonl(str(out_dir / "plan.jsonl"))
    events = read_jsonl(str(out_dir / "events.jsonl"))
    present_types = {r["type"] for r in plan_recs}
    assert present_types == set(PLAN_TYPES.keys())
    assert len(events) > 0
    assert run_all_checks(plan_recs, pack, "2027-01-01T00:00:00-08:00").passed is True
