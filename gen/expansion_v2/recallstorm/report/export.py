"""Export store packets, DC packets, CSVs, Markdown, and ZIP archives."""
from __future__ import annotations

import csv
from dataclasses import dataclass
import json
from pathlib import Path
import zipfile

from recallstorm.core.jsonl import write_jsonl
from recallstorm.report.summary import drill_summary, summary_to_markdown


@dataclass
class Exporter:
    """Multi-format exporter for Recall Storm execution plans."""

    out_dir: str


def export_csv(rows: list[dict], out_path: str) -> int:
    """Write a list of flat dictionaries to a CSV file at out_path."""
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        p.write_text("", encoding="utf-8")
        return 0
    fieldnames = list(rows[0].keys())
    with p.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return len(rows)


def export_markdown(records: list[dict], out_path: str) -> str:
    """Write a Markdown drill summary to out_path and return the Markdown text."""
    md = summary_to_markdown(drill_summary(records))
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(md, encoding="utf-8")
    return md


def export_evidence(records: list[dict], out_path: str) -> int:
    """Export all 'evidence' records to a JSONL file."""
    evs = [r for r in records if r.get("type") == "evidence"]
    return write_jsonl(out_path, evs)


def export_manifests(records: list[dict], out_path: str) -> int:
    """Export all 'route_manifest' records to a JSONL file."""
    mnfs = [r for r in records if r.get("type") == "route_manifest"]
    return write_jsonl(out_path, mnfs)


def export_store_packets(records: list[dict], out_dir: str) -> dict[str, str]:
    """Write per-store JSON packets containing playbook, tasks, and exceptions."""
    base = Path(out_dir)
    base.mkdir(parents=True, exist_ok=True)
    playbooks = {r["store_id"]: r for r in records if r.get("type") == "store_playbook"}
    paths: dict[str, str] = {}
    for st_id, pb in sorted(playbooks.items()):
        packet = {
            "store_id": st_id,
            "playbook": pb,
            "tasks": [r for r in records if r.get("type") == "shelf_task" and r.get("store_id") == st_id],
            "exceptions": [r for r in records if r.get("type") == "exception" and r.get("store_id") == st_id],
        }
        fp = base / f"store_{st_id}.json"
        fp.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
        paths[st_id] = str(fp)
    return paths


def export_dc_packets(records: list[dict], out_dir: str) -> dict[str, str]:
    """Write per-DC JSON packets containing allocations and route manifests."""
    base = Path(out_dir)
    base.mkdir(parents=True, exist_ok=True)
    dcs = sorted(
        {str(r["dc_id"]) for r in records if r.get("type") in {"allocation", "route_manifest"} and r.get("dc_id")}
    )
    paths: dict[str, str] = {}
    for dc_id in dcs:
        packet = {
            "dc_id": dc_id,
            "allocations": [r for r in records if r.get("type") == "allocation" and r.get("dc_id") == dc_id],
            "manifests": [r for r in records if r.get("type") == "route_manifest" and r.get("dc_id") == dc_id],
        }
        fp = base / f"dc_{dc_id}.json"
        fp.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
        paths[dc_id] = str(fp)
    return paths


def export_index(records: list[dict]) -> dict:
    """Build an export index of record counts by type."""
    counts: dict[str, int] = {}
    for r in records:
        t = str(r.get("type", "unknown"))
        counts[t] = counts.get(t, 0) + 1
    return {"total_records": len(records), "by_type": counts}


def export_zip(records: list[dict], zip_path: str) -> str:
    """Write plan.jsonl and summary.json into a ZIP archive at zip_path."""
    p = Path(zip_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(p, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        lines = "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n"
        zf.writestr("plan.jsonl", lines)
        zf.writestr("summary.json", json.dumps(drill_summary(records), indent=2, sort_keys=True))
    return str(p)
