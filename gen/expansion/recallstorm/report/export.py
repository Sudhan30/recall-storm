"""Export store execution packets, DC packets, CSV tables, Markdown, and ZIP archives."""
from __future__ import annotations

import csv
import zipfile
from dataclasses import dataclass
from pathlib import Path
from recallstorm.core.jsonl import write_jsonl
from recallstorm.report.summary import drill_summary, summary_to_markdown


@dataclass(frozen=True)
class Exporter:
    """Exports plan artifacts to disk."""

    out_dir: str


def export_csv(records: list[dict], rec_type: str, out_path: str | Path) -> int:
    """Export records of a given PLAN_TYPES rec_type to a CSV file."""
    filtered = [r for r in records if r.get("type") == rec_type]
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not filtered:
        p.write_text("", encoding="utf-8")
        return 0
    fieldnames = list(filtered[0].keys())
    with p.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in filtered:
            writer.writerow(r)
    return len(filtered)


def export_markdown(records: list[dict], out_path: str | Path) -> int:
    """Export an executive Markdown summary of plan records to out_path."""
    md = summary_to_markdown(drill_summary(records))
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(md, encoding="utf-8")
    return len(md)


def export_store_packets(records: list[dict], out_dir: str | Path) -> list[str]:
    """Write per-store JSONL execution packets containing each store's playbook, tasks, and exceptions."""
    base = Path(out_dir)
    base.mkdir(parents=True, exist_ok=True)
    stores = sorted({str(r["store_id"]) for r in records if "store_id" in r})
    written: list[str] = []
    for st_id in stores:
        st_recs = [r for r in records if r.get("store_id") == st_id]
        fpath = base / f"store_{st_id}.jsonl"
        write_jsonl(fpath, st_recs)
        written.append(str(fpath))
    return written


def export_dc_packets(records: list[dict], out_dir: str | Path) -> list[str]:
    """Write per-DC JSONL packets containing allocations and route manifests."""
    base = Path(out_dir)
    base.mkdir(parents=True, exist_ok=True)
    dcs = sorted({str(r["dc_id"]) for r in records if "dc_id" in r})
    written: list[str] = []
    for dc_id in dcs:
        dc_recs = [r for r in records if r.get("dc_id") == dc_id]
        fpath = base / f"dc_{dc_id}.jsonl"
        write_jsonl(fpath, dc_recs)
        written.append(str(fpath))
    return written


def export_evidence(records: list[dict], out_path: str | Path) -> int:
    """Export all evidence records to a JSONL file."""
    evs = [r for r in records if r.get("type") == "evidence"]
    return write_jsonl(out_path, evs)


def export_manifests(records: list[dict], out_path: str | Path) -> int:
    """Export all route_manifest records to a JSONL file."""
    mnfs = [r for r in records if r.get("type") == "route_manifest"]
    return write_jsonl(out_path, mnfs)


def export_zip(records: list[dict], zip_path: str | Path) -> str:
    """Bundle plan.jsonl and summary.md into a ZIP archive and return zip_path string."""
    zp = Path(zip_path)
    zp.parent.mkdir(parents=True, exist_ok=True)
    md = summary_to_markdown(drill_summary(records))
    from recallstorm.core.jsonl import stable_dumps
    jsonl_text = "\n".join(stable_dumps(r) for r in records) + "\n"
    with zipfile.ZipFile(zp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("plan.jsonl", jsonl_text)
        zf.writestr("summary.md", md)
    return str(zp)


def export_index(files: list[str]) -> dict:
    """Build an index dictionary of exported artifact file paths."""
    return {"file_count": len(files), "files": sorted(files)}
