"""Generate drill summaries, SKU verdict tables, and store task tables."""
from __future__ import annotations

from dataclasses import dataclass
import json

from contract import Action, Verdict


@dataclass
class SummaryReport:
    """High-level summary report of a Recall Storm execution plan."""

    run_id: str
    verdict_counts: dict[str, int]
    action_counts: dict[str, int]
    store_count: int


def counts_by_verdict(records: list[dict]) -> dict[str, int]:
    """Count sku_verdict records by Verdict value."""
    counts = {v.value: 0 for v in Verdict}
    for r in records:
        if r.get("type") == "sku_verdict":
            v = str(r.get("verdict", "KEEP"))
            counts[v] = counts.get(v, 0) + 1
    return counts


def counts_by_action(records: list[dict]) -> dict[str, int]:
    """Count shelf_task records by Action value."""
    counts = {a.value: 0 for a in Action}
    for r in records:
        if r.get("type") == "shelf_task":
            act = str(r.get("action", "PULL"))
            counts[act] = counts.get(act, 0) + 1
    return counts


def sku_table(records: list[dict]) -> list[dict]:
    """Extract sorted table of SKU verdicts."""
    rows = [
        {
            "sku_id": r["sku_id"],
            "gtin": r.get("gtin", ""),
            "verdict": r["verdict"],
            "additive": r.get("additive"),
            "rule_ids": r.get("rule_ids", []),
        }
        for r in records
        if r.get("type") == "sku_verdict"
    ]
    return sorted(rows, key=lambda x: str(x["sku_id"]))


def store_table(records: list[dict]) -> list[dict]:
    """Extract sorted table of store playbooks."""
    rows = [
        {
            "store_id": r["store_id"],
            "format": r.get("format", ""),
            "deadline": r.get("deadline", ""),
            "tasks": r.get("counts", {}).get("tasks", 0),
            "units": r.get("counts", {}).get("units", 0),
        }
        for r in records
        if r.get("type") == "store_playbook"
    ]
    return sorted(rows, key=lambda x: str(x["store_id"]))


def drill_summary(records: list[dict]) -> dict:
    """Build a comprehensive summary dictionary from plan.jsonl records."""
    run_rec = next((r for r in records if r.get("type") == "run"), {})
    return {
        "run_id": run_rec.get("run_id", "UNKNOWN"),
        "scenario_id": run_rec.get("scenario_id", "UNKNOWN"),
        "verdicts": counts_by_verdict(records),
        "actions": counts_by_action(records),
        "stores": len(store_table(records)),
        "allocations": sum(1 for r in records if r.get("type") == "allocation"),
        "manifests": sum(1 for r in records if r.get("type") == "route_manifest"),
    }


def summary_to_json(summary: dict) -> str:
    """Serialize summary dictionary to formatted JSON."""
    return json.dumps(summary, indent=2, sort_keys=True)


def summary_to_markdown(summary: dict) -> str:
    """Format a drill summary as a Markdown report."""
    v = summary.get("verdicts", {})
    a = summary.get("actions", {})
    return (
        f"# Recall Storm Drill Summary ({summary.get('run_id')})\n\n"
        f"- Scenario: `{summary.get('scenario_id')}`\n"
        f"- Stores: {summary.get('stores', 0)}\n"
        f"- Verdicts: PULL={v.get('PULL', 0)}, HOLD_VERIFY={v.get('HOLD_VERIFY', 0)}, KEEP={v.get('KEEP', 0)}\n"
        f"- Tasks: PULL={a.get('PULL', 0)}, PLACE_SUB={a.get('PLACE_SUB', 0)}, TAG_FLASH={a.get('TAG_FLASH', 0)}, HOLD_VERIFY={a.get('HOLD_VERIFY', 0)}\n"
    )


def compare_runs(r1: list[dict], r2: list[dict]) -> dict:
    """Compare two sets of plan.jsonl records."""
    s1, s2 = drill_summary(r1), drill_summary(r2)
    return {
        "pull_delta": s2["verdicts"]["PULL"] - s1["verdicts"]["PULL"],
        "store_delta": s2["stores"] - s1["stores"],
    }
