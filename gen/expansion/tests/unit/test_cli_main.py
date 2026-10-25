"""Unit tests for recallstorm.cli.main."""
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
from recallstorm.core.errors import DataValidationError, ScenarioError


def test_cli_commands(tmp_path):
    parser = build_parser()
    assert parser is not None
    out_dir = tmp_path / "run_out"
    rc = main(["run", "--scenario", "ca_red3", "--data", "data", "--out", str(out_dir)])
    assert rc == 0
    plan_path = out_dir / "plan.jsonl"
    events_path = out_dir / "events.jsonl"
    assert plan_path.exists()
    assert events_path.exists()

    assert main(["validate", "--data", "data", "--plan", str(plan_path)]) == 0
    assert main(["stats", "--plan", str(plan_path)]) == 0
    assert main(["explain", "--plan", str(plan_path)]) == 0
    rep_out = tmp_path / "replayed.jsonl"
    assert main(["replay", "--plan", str(plan_path), "--out", str(rep_out)]) == 0
    assert rep_out.exists()
    assert main(["scenarios", "--data", "data"]) == 0

    assert exit_code_for(None) == 0
    assert exit_code_for(ScenarioError("bad")) == 2
    assert exit_code_for(DataValidationError("bad")) == 3

    args_scen = parser.parse_args(["scenarios", "--data", "data"])
    assert cmd_scenarios(args_scen) == 0
    args_val = parser.parse_args(["validate", "--data", "data"])
    assert cmd_validate(args_val) == 0
    args_st = parser.parse_args(["stats", "--plan", str(plan_path)])
    assert cmd_stats(args_st) == 0
    args_ex = parser.parse_args(["explain", "--plan", str(plan_path)])
    assert cmd_explain(args_ex) == 0
    args_rp = parser.parse_args(["replay", "--plan", str(plan_path), "--out", str(rep_out)])
    assert cmd_replay(args_rp) == 0
    args_rn = parser.parse_args(["run", "--scenario", "ca_red3", "--data", "data", "--out", str(tmp_path / "r2")])
    assert cmd_run(args_rn) == 0
