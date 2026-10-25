"""Executive drill summary, store/SKU tables, and Markdown/JSON formatters."""
from __future__ import annotations

import json
from dataclasses import dataclass
from contract import Action, Verdict


@dataclass(frozen=True)
class SummaryReport:
    """High-level summary of a recall execution plan."""

    run_id: str
    verdicts: dict[str, int]
    actions: dict[str, int]
    store_count: int


def counts_by_verdict(records: list[dict]) -> dict[str, int]:
    """Count sku_verdict records by Verdict value."""
    counts = {Verdict.PULL.value: 0, Verdict.HOLD_VERIFY.value: 0, Verdict.KEEP.value: 0}
    for r in records:
        if r.get("type") == "sku_verdict":
            v = str(r.get("verdict", ""))
            counts[v] = counts.get(v, 0) + 1
    return counts


def counts_by_action(records: list[dict]) -> dict[str, int]:
    """Count shelf_task records by Action value."""
    counts = {a.value: 0 for a in Action}
    for r in records:
        if r.get("type") == "shelf_task":
            act = str(r.get("action", ""))
            counts[act] = counts.get(act, 0) + 1
    return counts


def store_table(records: list[dict]) -> list[dict]:
    """Build a summary table of store playbooks."""
    out: list[dict] = []
    for r in records:
        if r.get("type") == "store_playbook":
            out.append(
                {
                    "store_id": r["store_id"],
                    "format": r["format"],
                    "deadline": r["deadline"],
                    "total_tasks": r.get("counts", {}).get("total_tasks", 0),
                    "associates": len(r.get("associate_ids", [])),
                    "exceptions": len(r.get("exception_ids", [])),
                }
            )
    return sorted(out, key=lambda x: str(x["store_id"]))


def sku_table(records: list[dict]) -> list[dict]:
    """Build a summary table of PULL and HOLD_VERIFY SKUs."""
    out: list[dict] = []
    for r in records:
        if r.get("type") == "sku_verdict" and r.get("verdict") != Verdict.KEEP.value:
            out.append(
                {
                    "sku_id": r["sku_id"],
                    "gtin": r["gtin"],
                    "verdict": r["verdict"],
                    "additive": r.get("additive"),
                    "rule_ids": r.get("rule_ids", []),
                }
            )
    return sorted(out, key=lambda x: str(x["sku_id"]))


def drill_summary(records: list[dict]) -> dict:
    """Compute a comprehensive summary dictionary from plan.jsonl records."""
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


def summary_to_markdown(summary: dict) -> str:
    """Format a drill_summary dictionary as a Markdown report."""
    v = summary.get("verdicts", {})
    a = summary.get("actions", {})
    return (
        f"# Recall Storm Drill Summary ({summary.get('scenario_id')})\n\n"
        f"- **Run ID**: `{summary.get('run_id')}`\n"
        f"- **Stores**: {summary.get('stores', 0)}\n"
        f"- **Verdicts**: PULL={v.get('PULL', 0)}, HOLD_VERIFY={v.get('HOLD_VERIFY', 0)}, KEEP={v.get('KEEP', 0)}\n"
        f"- **Tasks**: PULL={a.get('PULL', 0)}, PLACE_SUB={a.get('PLACE_SUB', 0)}, "
        f"TAG_FLASH={a.get('TAG_FLASH', 0)}, HOLD_VERIFY={a.get('HOLD_VERIFY', 0)}\n"
        f"- **Allocations**: {summary.get('allocations', 0)}\n"
        f"- **Route Manifests**: {summary.get('manifests', 0)}\n"
    )


def summary_to_json(summary: dict) -> str:
    """Serialize a drill_summary dictionary to formatted JSON."""
    return json.dumps(summary, indent=2, sort_keys=True)


def compare_runs(r1: list[dict], r2: list[dict]) -> dict:
    """Compare two plan record lists and return delta counts."""
    s1 = drill_summary(r1)
    s2 = drill_summary(r2)
    return {
        "pull_delta": s2["verdicts"]["PULL"] - s1["verdicts"]["PULL"],
        "store_delta": s2["stores"] - s1["stores"],
    }
