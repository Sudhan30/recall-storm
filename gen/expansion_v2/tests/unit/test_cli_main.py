"""Unit tests for recallstorm.cli.main."""
from datetime import datetime
from contract import Truck
from recallstorm.cli.main import (
    build_parser,
    cmd_explain,
    cmd_replay,
    cmd_run,
    cmd_scenarios,
    cmd_stats,
    cmd_validate,
    exit_code_for,
    main,
)
from recallstorm.core.jsonl import read_jsonl
from tests.unit.test_plan_assemble import _sample_pack


def test_cli_commands(tmp_path, monkeypatch):
    pack = _sample_pack()
    pack.trucks.append(Truck("DC_CENTRAL-T0", "DC_CENTRAL", 3400.0, 40000.0, datetime.fromisoformat("2026-12-31T08:00:00-08:00")))
    monkeypatch.setattr("recallstorm.cli.main.load_datapack_extended", lambda d: pack)

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "scenario_ca_red3.json").write_text(
        '{"scenario_id": "ca_red3", "state": "CA", "rule_ids": ["CA_AB418_RED3"], "as_of": "2026-12-30T18:00:00-08:00", "deadline": "2027-01-01T00:00:00-08:00"}',
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"

    assert exit_code_for(True) == 0
    assert exit_code_for(False) == 1
    assert build_parser() is not None
    assert main(["run", "--scenario", "ca_red3", "--data", str(data_dir), "--out", str(out_dir)]) == 0
    assert (out_dir / "plan.jsonl").exists()
    assert (out_dir / "events.jsonl").exists()
    assert len(read_jsonl(str(out_dir / "plan.jsonl"))) > 0

    assert cmd_validate(str(data_dir)) == 0
    assert cmd_stats(str(data_dir)) == 0
    assert cmd_explain(str(out_dir / "plan.jsonl"), "FDC1034191") == 0
    assert cmd_replay(str(out_dir / "plan.jsonl"), str(out_dir / "events2.jsonl")) == 0
    assert cmd_scenarios(str(data_dir)) == 0
    assert cmd_run("ca_red3", str(data_dir), str(out_dir / "run2")) == 0
