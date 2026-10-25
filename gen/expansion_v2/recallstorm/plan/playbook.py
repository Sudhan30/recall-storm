"""Build store_playbook records summarizing store execution."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from contract import Action, Store
from recallstorm.core.clock import iso_with_offset


@dataclass
class PlaybookBuilder:
    """Builder for store_playbook records."""

    store: Store


def playbook_counts(tasks: list[dict]) -> dict[str, int]:
    """Compute counts of tasks by Action plus total_units."""
    counts = {a.value: 0 for a in Action}
    total_units = 0
    for t in tasks:
        act = str(t.get("action", "PULL"))
        counts[act] = counts.get(act, 0) + 1
        total_units += int(t.get("qty_units", 0))
    counts["tasks"] = len(tasks)
    counts["units"] = total_units
    return counts


def playbook_windows(tasks: list[dict], deadline: datetime) -> list[list[str]]:
    """Compute overall execution windows for a store's tasks strictly before deadline."""
    if not tasks:
        s = deadline - timedelta(hours=4)
        e = deadline - timedelta(hours=3)
        return [[iso_with_offset(s), iso_with_offset(e)]]
    starts = [datetime.fromisoformat(t["window"][0]) for t in tasks if t.get("window")]
    ends = [datetime.fromisoformat(t["window"][1]) for t in tasks if t.get("window")]
    if not starts or not ends:
        s = deadline - timedelta(hours=4)
        e = deadline - timedelta(hours=3)
        return [[iso_with_offset(s), iso_with_offset(e)]]
    min_s = min(starts)
    max_e = min(max(ends), deadline - timedelta(minutes=1))
    return [[iso_with_offset(min_s), iso_with_offset(max_e)]]


def playbook_deadline(store: Store, deadline: datetime) -> str:
    """Return the store's local ISO deadline string."""
    return iso_with_offset(deadline, store.tz)


def playbook_exceptions(exceptions: list[dict], store_id: str) -> list[str]:
    """Return exc_ids belonging to store_id."""
    return [str(e["exc_id"]) for e in exceptions if e.get("store_id") == store_id and "exc_id" in e]


def playbook_manifests(manifests: list[dict], store_id: str) -> list[str]:
    """Return manifest_ids whose stops include store_id."""
    out: list[str] = []
    for m in manifests:
        stops = m.get("stops") or []
        if any((s.get("store_id") if isinstance(s, dict) else getattr(s, "store_id", None)) == store_id for s in stops):
            out.append(str(m["manifest_id"]))
    return out


def build_playbook(
    store: Store,
    tasks: list[dict],
    exceptions: list[dict],
    manifests: list[dict],
    deadline: datetime,
) -> dict:
    """Build a plan.jsonl 'store_playbook' record for store."""
    st_tasks = [t for t in tasks if t.get("store_id") == store.store_id]
    assoc_ids = sorted({str(t["associate_id"]) for t in st_tasks if t.get("associate_id")})
    return {
        "type": "store_playbook",
        "store_id": store.store_id,
        "format": store.format.value,
        "deadline": playbook_deadline(store, deadline),
        "windows": playbook_windows(st_tasks, deadline),
        "counts": playbook_counts(st_tasks),
        "associate_ids": assoc_ids,
        "exception_ids": playbook_exceptions(exceptions, store.store_id),
        "manifest_ids": playbook_manifests(manifests, store.store_id),
        "src": "recallstorm/plan/playbook.py",
    }


def playbook_to_record(playbook: dict) -> dict:
    """Ensure playbook dict has 'type' and 'src' fields set."""
    out = dict(playbook)
    out["type"] = "store_playbook"
    out.setdefault("src", "recallstorm/plan/playbook.py")
    return out


def playbook_summary(playbooks: list[dict]) -> dict:
    """Summarize a list of store_playbook records."""
    return {
        "store_count": len(playbooks),
        "total_tasks": sum(p.get("counts", {}).get("tasks", 0) for p in playbooks),
    }
