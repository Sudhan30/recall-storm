"""CLI entrypoint for Recall Storm (`python -m recallstorm run ...`)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from contract import load_datapack
from recallstorm.plan import build_plan, write_plan_jsonl
from recallstorm.sim import simulate_events, write_events_jsonl


def _load_scenario(data_dir: Path, scenario_id: str) -> dict:
    candidates = [
        data_dir / f"scenario_{scenario_id}.json",
        data_dir / f"{scenario_id}.json",
    ]
    for c in candidates:
        if c.exists():
            with c.open("r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError(f"Scenario file not found for scenario '{scenario_id}' in {data_dir}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="recallstorm", description="Recall Storm compliance drill CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a recall scenario and emit plan.jsonl and events.jsonl")
    run_parser.add_argument("--scenario", required=True, help="Scenario ID (e.g. ca_red3)")
    run_parser.add_argument("--data", required=True, help="Path to data directory")
    run_parser.add_argument("--out", required=True, help="Path to output directory")

    args = parser.parse_args(argv)

    if args.command == "run":
        data_dir = Path(args.data)
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)

        scenario = _load_scenario(data_dir, args.scenario)
        pack = load_datapack(str(data_dir))

        plan_records = build_plan(pack, scenario)
        events = simulate_events(plan_records)

        write_plan_jsonl(plan_records, out_dir / "plan.jsonl")
        write_events_jsonl(events, out_dir / "events.jsonl")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
