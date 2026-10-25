"""Command-line interface for Recall Storm (`python -m recallstorm run --scenario <id> --data <dir> --out <dir>`)."""
from __future__ import annotations

import argparse
from pathlib import Path
from contract import Sku, Store, Truck, load_datapack
from recallstorm.core.config import config_to_dict, get_scenario_path, load_config
from recallstorm.core.errors import (
    DataValidationError,
    RecallStormError,
    ScenarioError,
    format_error,
)
from recallstorm.core.jsonl import read_jsonl
from recallstorm.core.validate import validate_datapack
from recallstorm.plan.assemble import assemble_plan, plan_to_jsonl
from recallstorm.plan.explain import plan_narrative
from recallstorm.report.checks import run_all_checks
from recallstorm.report.summary import drill_summary, summary_to_json
from recallstorm.route.packing import manifest_to_record, pack_returns
from recallstorm.sim.events import events_to_jsonl
from recallstorm.sim.replay import simulate_plan


def exit_code_for(exc: BaseException | None) -> int:
    """Map an exception to a deterministic CLI exit code."""
    if exc is None:
        return 0
    if isinstance(exc, ScenarioError):
        return 2
    if isinstance(exc, DataValidationError):
        return 3
    if isinstance(exc, RecallStormError):
        return 4
    return 1


def _pack_manifests_callback(
    pulled_cases: dict[tuple[str, str], int],
    skus: list[Sku],
    trucks: list[Truck],
    stores: list[Store],
):
    manifests = pack_returns(pulled_cases, skus, trucks, stores)
    trucks_by_id = {t.truck_id: t for t in trucks}
    recs = [manifest_to_record(m, trucks_by_id[m.truck_id]) for m in manifests]
    return manifests, recs


def build_parser() -> argparse.ArgumentParser:
    """Build the ArgumentParser for `python -m recallstorm`."""
    parser = argparse.ArgumentParser(prog="recallstorm", description="Recall Storm compliance & store execution platform")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Run a recall scenario and emit plan.jsonl and events.jsonl")
    p_run.add_argument("--scenario", required=True, help="Scenario ID (e.g. ca_red3)")
    p_run.add_argument("--data", default="data", help="Data directory")
    p_run.add_argument("--out", required=True, help="Output directory")

    p_val = sub.add_parser("validate", help="Validate a DataPack directory or plan.jsonl")
    p_val.add_argument("--data", default="data", help="Data directory")
    p_val.add_argument("--plan", default=None, help="Optional plan.jsonl path")

    p_stats = sub.add_parser("stats", help="Print summary statistics for a plan.jsonl")
    p_stats.add_argument("--plan", required=True, help="Path to plan.jsonl")

    p_exp = sub.add_parser("explain", help="Print narrative explanation of a plan.jsonl")
    p_exp.add_argument("--plan", required=True, help="Path to plan.jsonl")

    p_rep = sub.add_parser("replay", help="Replay shelf tasks from plan.jsonl into events.jsonl")
    p_rep.add_argument("--plan", required=True, help="Path to plan.jsonl")
    p_rep.add_argument("--out", required=True, help="Path to events.jsonl")

    p_scen = sub.add_parser("scenarios", help="List available scenario files in data directory")
    p_scen.add_argument("--data", default="data", help="Data directory")

    return parser


def cmd_run(args: argparse.Namespace) -> int:
    """Execute `recallstorm run --scenario <id> --data <dir> --out <dir>`."""
    scen_path = get_scenario_path(args.data, args.scenario)
    cfg = load_config(scen_path)
    pack = load_datapack(args.data)
    scen_dict = config_to_dict(cfg)

    records = assemble_plan(pack, scen_dict, manifest_packer=_pack_manifests_callback)
    events = simulate_plan(records)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_to_jsonl(records, out_dir / "plan.jsonl")
    events_to_jsonl(events, out_dir / "events.jsonl")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Execute `recallstorm validate`."""
    pack = load_datapack(args.data)
    issues = validate_datapack(pack)
    if args.plan:
        records = read_jsonl(args.plan)
        rep = run_all_checks(records, pack, "2027-01-01T00:00:00-08:00")
        if not rep.passed:
            return 3
    return 0 if not issues else 3


def cmd_stats(args: argparse.Namespace) -> int:
    """Execute `recallstorm stats`."""
    records = read_jsonl(args.plan)
    print(summary_to_json(drill_summary(records)))
    return 0


def cmd_explain(args: argparse.Namespace) -> int:
    """Execute `recallstorm explain`."""
    records = read_jsonl(args.plan)
    print(plan_narrative(records))
    return 0


def cmd_replay(args: argparse.Namespace) -> int:
    """Execute `recallstorm replay`."""
    records = read_jsonl(args.plan)
    events = simulate_plan(records)
    events_to_jsonl(events, args.out)
    return 0


def cmd_scenarios(args: argparse.Namespace) -> int:
    """Execute `recallstorm scenarios`."""
    base = Path(args.data)
    if not base.exists():
        raise ScenarioError(f"Data directory not found: {base}")
    files = sorted(p.name for p in base.glob("scenario_*.json"))
    for f in files:
        print(f)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point returning exit code."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        dispatch = {
            "run": cmd_run,
            "validate": cmd_validate,
            "stats": cmd_stats,
            "explain": cmd_explain,
            "replay": cmd_replay,
            "scenarios": cmd_scenarios,
        }
        handler = dispatch.get(args.command)
        if handler is None:
            return 1
        return handler(args)
    except BaseException as exc:
        if isinstance(exc, SystemExit):
            return int(exc.code) if isinstance(exc.code, int) else 1
        print(format_error(exc))
        return exit_code_for(exc)
