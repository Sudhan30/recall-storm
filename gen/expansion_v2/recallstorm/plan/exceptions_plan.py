"""Generate exception records and linked shelf tasks for store notes."""
from __future__ import annotations

from dataclasses import dataclass

from contract import ExceptionKind, StoreNote
from recallstorm.core.ids import make_exc_id
from recallstorm.store.exceptions import exception_kind_for_text, resolve_exception


@dataclass
class ExceptionPlanner:
    """Planner converting StoreNotes into plan.jsonl exception records."""

    notes: list[StoreNote]


def _make_exc(note: StoreNote, kind: ExceptionKind, task_ids: list[str]) -> dict:
    return {
        "type": "exception",
        "exc_id": make_exc_id(note.store_id, note.note_id),
        "store_id": note.store_id,
        "kind": kind.value,
        "note_id": note.note_id,
        "resolution": resolve_exception(kind, note),
        "task_ids": list(task_ids),
        "src": "recallstorm/plan/exceptions_plan.py",
    }


def dsd_exception_task(note: StoreNote, task_ids: list[str]) -> dict:
    """Build a DSD_VENDOR_PULL exception record."""
    return _make_exc(note, ExceptionKind.DSD_VENDOR_PULL, task_ids)


def endcap_exception_task(note: StoreNote, task_ids: list[str]) -> dict:
    """Build an ENDCAP_DISPLAY exception record."""
    return _make_exc(note, ExceptionKind.ENDCAP_DISPLAY, task_ids)


def topstock_exception_task(note: StoreNote, task_ids: list[str]) -> dict:
    """Build a TOPSTOCK exception record."""
    return _make_exc(note, ExceptionKind.TOPSTOCK, task_ids)


def totes_exception_task(note: StoreNote, task_ids: list[str]) -> dict:
    """Build a PICKUP_TOTES exception record."""
    return _make_exc(note, ExceptionKind.PICKUP_TOTES, task_ids)


def planogram_exception_task(note: StoreNote, task_ids: list[str]) -> dict:
    """Build a NOT_ON_PLANOGRAM exception record."""
    return _make_exc(note, ExceptionKind.NOT_ON_PLANOGRAM, task_ids)


def unclear_label_task(note: StoreNote, task_ids: list[str]) -> dict:
    """Build an UNCLEAR_LABEL exception record."""
    return _make_exc(note, ExceptionKind.UNCLEAR_LABEL, task_ids)


def exception_records(notes: list[StoreNote], tasks_by_store: dict[str, list[dict]]) -> list[dict]:
    """Generate plan.jsonl 'exception' records for all StoreNotes linked to store task IDs."""
    out: list[dict] = []
    for n in sorted(notes, key=lambda x: (x.store_id, x.note_id)):
        st_tasks = tasks_by_store.get(n.store_id, [])
        tids = [str(t["task_id"]) for t in st_tasks[:2] if "task_id" in t]
        kind = exception_kind_for_text(n.text)
        out.append(_make_exc(n, kind, tids))
    return out


def exception_tasks(
    notes: list[StoreNote], store_tasks: list[dict]
) -> tuple[list[dict], list[dict]]:
    """Group store_tasks by store and return (exception_records, store_tasks)."""
    by_store: dict[str, list[dict]] = {}
    for t in store_tasks:
        by_store.setdefault(str(t.get("store_id", "")), []).append(t)
    excs = exception_records(notes, by_store)
    return (excs, store_tasks)
