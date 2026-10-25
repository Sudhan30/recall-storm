"""Build PLAN_TYPES['store_playbook'] records for every store in a recall scenario."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from contract import Action, RouteManifest, Store
from recallstorm.core.clock import iso_with_offset
from recallstorm.core.jsonl import record_with_src


@dataclass(frozen=True)
class PlaybookBuilder:
    """Builds store_playbook records."""

    deadline: datetime


def playbook_counts(tasks: list[dict]) -> dict[str, int]:
    """Count shelf tasks per Action plus total_tasks and total_units."""
    counts = {
        Action.PULL.value: 0,
        Action.HOLD_VERIFY.value: 0,
        Action.PLACE_SUB.value: 0,
        Action.TAG_FLASH.value: 0,
    }
    for t in tasks:
        act = str(t.get("action", ""))
        if act in counts:
            counts[act] += 1
    counts["total_tasks"] = len(tasks)
    return counts


def playbook_windows(tasks: list[dict], default_window: list[str]) -> list[list[str]]:
    """Aggregate the overall [min_start, max_end] window for a store's playbook."""
    if not tasks:
        return [list(default_window)]
    starts = [t["window"][0] for t in tasks if "window" in t and len(t["window"]) == 2]
    ends = [t["window"][1] for t in tasks if "window" in t and len(t["window"]) == 2]
    if not starts or not ends:
        return [list(default_window)]
    return [[min(starts), max(ends)]]


def playbook_deadline(deadline: datetime | str, tz_name: str = "America/Los_Angeles") -> str:
    """Format the store playbook deadline in the store's local timezone."""
    dt = datetime.fromisoformat(deadline) if isinstance(deadline, str) else deadline
    return iso_with_offset(dt, tz_name)


def playbook_exceptions(exceptions: list[dict], store_id: str) -> list[str]:
    """Return sorted exc_ids belonging to store_id."""
    return sorted(str(e["exc_id"]) for e in exceptions if e.get("store_id") == store_id and "exc_id" in e)


def playbook_manifests(manifests: list[RouteManifest] | list[dict], store_id: str) -> list[str]:
    """Return sorted manifest_ids that include a stop at store_id."""
    out: list[str] = []
    for m in manifests:
        if isinstance(m, RouteManifest):
            if any(st.store_id == store_id for st in m.stops):
                out.append(m.manifest_id)
        elif isinstance(m, dict):
            stops = m.get("stops", [])
            if any(s.get("store_id") == store_id for s in stops):
                out.append(str(m["manifest_id"]))
    return sorted(set(out))


def build_playbook(
    store: Store,
    tasks: list[dict],
    exceptions: list[dict],
    manifests: list[RouteManifest] | list[dict],
    deadline: datetime | str,
    default_window: list[str] | None = None,
    fallback_associate_ids: list[str] | None = None,
) -> dict:
    """Build a validated 'store_playbook' plan.jsonl record for a Store."""
    st_tasks = [t for t in tasks if t.get("store_id") == store.store_id]
    assoc_ids = sorted({str(t["associate_id"]) for t in st_tasks if t.get("associate_id")})
    if not assoc_ids and fallback_associate_ids:
        assoc_ids = sorted(set(fallback_associate_ids))
    def_win = default_window or ["2026-12-30T22:00:00-08:00", "2026-12-31T06:00:00-08:00"]
    payload = {
        "store_id": store.store_id,
        "format": store.format.value,
        "deadline": playbook_deadline(deadline, store.tz),
        "windows": playbook_windows(st_tasks, def_win),
        "counts": playbook_counts(st_tasks),
        "associate_ids": assoc_ids,
        "exception_ids": playbook_exceptions(exceptions, store.store_id),
        "manifest_ids": playbook_manifests(manifests, store.store_id),
    }
    return record_with_src(payload, "store_playbook", "recallstorm/plan/playbook.py")


def playbook_to_record(playbook: dict) -> dict:
    """Validate and return a store_playbook record."""
    payload = {k: v for k, v in playbook.items() if k not in ("type", "src")}
    return record_with_src(payload, "store_playbook", "recallstorm/plan/playbook.py")


def playbook_summary(playbooks: list[dict]) -> dict:
    """Summarize total stores and task counts across playbooks."""
    total_tasks = sum(p.get("counts", {}).get("total_tasks", 0) for p in playbooks)
    return {"store_count": len(playbooks), "total_tasks": total_tasks}
