"""CLI entry point supporting run, validate, stats, explain, replay, and scenarios."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path

from recallstorm.core.config import get_scenario_path
from recallstorm.core.jsonl import read_jsonl
from recallstorm.core.validate import validate_datapack
from recallstorm.ingest.manifest_io import datapack_stats, load_datapack_extended
from recallstorm.plan.assemble import assemble_plan, plan_to_jsonl
from recallstorm.plan.explain import explain_sku, plan_narrative
from recallstorm.report.checks import run_all_checks
from recallstorm.route.packing import manifest_to_record, pack_returns
from recallstorm.route.returns import returned_cases
from recallstorm.rules.engine import evaluate_sku
from recallstorm.sim.events import events_to_jsonl
from recallstorm.sim.replay import simulate_plan
from recallstorm.store.exceptions import dsd_vendor_pull


def exit_code_for(ok: bool) -> int:
    """Return 0 when ok is True, else 1."""
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    """Build the Recall Storm CLI ArgumentParser."""
    parser = argparse.ArgumentParser(prog="recallstorm", description="Recall Storm Platform CLI")
    sub = parser.add_subparsers(dest="command")

    p_run = sub.add_parser("run", help="Run a recall scenario and emit plan.jsonl and events.jsonl")
    p_run.add_argument("--scenario", required=True, help="Scenario ID (e.g. ca_red3)")
    p_run.add_argument("--data", required=True, help="Data directory path")
    p_run.add_argument("--out", required=True, help="Output directory path")

    p_val = sub.add_parser("validate", help="Validate a datapack directory")
    p_val.add_argument("--data", required=True, help="Data directory path")

    p_sts = sub.add_parser("stats", help="Print datapack statistics")
    p_sts.add_argument("--data", required=True, help="Data directory path")

    p_exp = sub.add_parser("explain", help="Explain a generated plan.jsonl")
    p_exp.add_argument("--plan", required=True, help="Path to plan.jsonl")
    p_exp.add_argument("--sku", default=None, help="Optional SKU ID to explain")

    p_rep = sub.add_parser("replay", help="Replay plan.jsonl into events.jsonl")
    p_rep.add_argument("--plan", required=True, help="Path to plan.jsonl")
    p_rep.add_argument("--out", required=True, help="Output events.jsonl path")

    p_scn = sub.add_parser("scenarios", help="List available scenarios in data directory")
    p_scn.add_argument("--data", required=True, help="Data directory path")

    return parser


def cmd_run(scenario_id: str, data_dir: str, out_dir: str) -> int:
    """Execute a scenario end-to-end and write out_dir/plan.jsonl and out_dir/events.jsonl."""
    pack = load_datapack_extended(data_dir)
    sc_path = Path(get_scenario_path(data_dir, scenario_id))
    if sc_path.exists():
        scenario = json.loads(sc_path.read_text(encoding="utf-8"))
    else:
        scenario = {
            "scenario_id": scenario_id,
            "state": "CA",
            "rule_ids": [r.rule_id for r in pack.rules],
            "as_of": pack.as_of.isoformat(),
            "deadline": "2027-01-01T00:00:00-08:00",
        }

    state = str(scenario.get("state", "CA"))
    rule_ids = set(scenario.get("rule_ids") or [r.rule_id for r in pack.rules])
    active_rules = [r for r in pack.rules if r.rule_id in rule_ids] or list(pack.rules)
    deadline_dt = datetime.fromisoformat(str(scenario.get("deadline", "2027-01-01T00:00:00-08:00")))

    sku_map = {s.sku_id: s for s in pack.skus}
    decisions = {s.sku_id: evaluate_sku(s, active_rules, state, deadline_dt) for s in pack.skus}
    dsd_stores = {n.store_id for n in pack.notes if dsd_vendor_pull(n)}
    pulled = returned_cases(pack.facings, decisions, sku_map, dsd_stores=dsd_stores)
    manifests = pack_returns(pulled, pack.skus, pack.trucks, pack.stores)
    trk_map = {t.truck_id: t for t in pack.trucks}
    mnf_recs = [manifest_to_record(m, trk_map[m.truck_id]) for m in manifests if m.truck_id in trk_map]

    records = assemble_plan(pack, scenario, manifests=mnf_recs)
    events = simulate_plan(records, deadline=deadline_dt)

    out_p = Path(out_dir)
    out_p.mkdir(parents=True, exist_ok=True)
    plan_to_jsonl(records, str(out_p / "plan.jsonl"))
    events_to_jsonl(events, str(out_p / "events.jsonl"))

    chk = run_all_checks(records, pack, str(scenario.get("deadline")))
    return exit_code_for(chk.passed)


def cmd_validate(data_dir: str) -> int:
    """Validate a datapack directory."""
    pack = load_datapack_extended(data_dir)
    issues = validate_datapack(pack)
    return exit_code_for(len(issues) == 0)


def cmd_stats(data_dir: str) -> int:
    """Compute datapack stats and return 0."""
    pack = load_datapack_extended(data_dir)
    stats = datapack_stats(pack)
    return exit_code_for(stats["skus"] >= 0)


def cmd_explain(plan_path: str, sku_id: str | None = None) -> int:
    """Explain a plan.jsonl file or a specific SKU verdict."""
    records = read_jsonl(plan_path)
    if sku_id:
        v_rec = next((r for r in records if r.get("type") == "sku_verdict" and r.get("sku_id") == sku_id), None)
        if not v_rec:
            return exit_code_for(False)
        explain_sku(v_rec)
        return exit_code_for(True)
    plan_narrative(records)
    return exit_code_for(len(records) > 0)


def cmd_replay(plan_path: str, out_events_path: str) -> int:
    """Replay shelf tasks from plan_path into out_events_path."""
    records = read_jsonl(plan_path)
    events = simulate_plan(records)
    events_to_jsonl(events, out_events_path)
    return exit_code_for(True)


def cmd_scenarios(data_dir: str) -> int:
    """List scenario_*.json files in data_dir."""
    p = Path(data_dir)
    if not p.exists():
        return exit_code_for(False)
    _ = sorted(f.name for f in p.glob("scenario_*.json"))
    return exit_code_for(True)


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        return cmd_run(args.scenario, args.data, args.out)
    if args.command == "validate":
        return cmd_validate(args.data)
    if args.command == "stats":
        return cmd_stats(args.data)
    if args.command == "explain":
        return cmd_explain(args.plan, args.sku)
    if args.command == "replay":
        return cmd_replay(args.plan, args.out)
    if args.command == "scenarios":
        return cmd_scenarios(args.data)
    parser.print_help()
    return 1
