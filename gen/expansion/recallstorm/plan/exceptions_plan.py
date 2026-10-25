"""Link StoreNotes to store shelf tasks and emit PLAN_TYPES['exception'] records."""
from __future__ import annotations

from dataclasses import dataclass
from contract import Action, ExceptionKind, StoreNote
from recallstorm.core.ids import make_exc_id
from recallstorm.core.jsonl import record_with_src
from recallstorm.store.exceptions import exception_kind_for_text, resolve_exception


@dataclass(frozen=True)
class ExceptionPlanner:
    """Planner that maps StoreNotes to exception records and linked shelf tasks."""

    notes: tuple[StoreNote, ...]


def _pull_task_ids(store_tasks: list[dict]) -> list[str]:
    ids = [str(t["task_id"]) for t in store_tasks if t.get("action") == Action.PULL.value and "task_id" in t]
    if not ids:
        ids = [str(t["task_id"]) for t in store_tasks if "task_id" in t]
    return ids[:3]


def dsd_exception_task(note: StoreNote, store_tasks: list[dict]) -> list[str]:
    """Return task_ids linked to a DSD_VENDOR_PULL exception."""
    return _pull_task_ids(store_tasks)


def endcap_exception_task(note: StoreNote, store_tasks: list[dict]) -> list[str]:
    """Return task_ids linked to an ENDCAP_DISPLAY exception."""
    return _pull_task_ids(store_tasks)


def topstock_exception_task(note: StoreNote, store_tasks: list[dict]) -> list[str]:
    """Return task_ids linked to a TOPSTOCK exception."""
    return _pull_task_ids(store_tasks)


def totes_exception_task(note: StoreNote, store_tasks: list[dict]) -> list[str]:
    """Return task_ids linked to a PICKUP_TOTES exception."""
    return _pull_task_ids(store_tasks)


def planogram_exception_task(note: StoreNote, store_tasks: list[dict]) -> list[str]:
    """Return task_ids linked to a NOT_ON_PLANOGRAM exception."""
    return _pull_task_ids(store_tasks)


def unclear_label_task(note: StoreNote, store_tasks: list[dict]) -> list[str]:
    """Return HOLD_VERIFY or PULL task_ids linked to an UNCLEAR_LABEL exception."""
    hold_ids = [str(t["task_id"]) for t in store_tasks if t.get("action") == Action.HOLD_VERIFY.value and "task_id" in t]
    return hold_ids[:3] if hold_ids else _pull_task_ids(store_tasks)


def exception_tasks(note: StoreNote, store_tasks: list[dict]) -> list[str]:
    """Dispatch by ExceptionKind to select linked task_ids for a StoreNote."""
    if not isinstance(note, StoreNote):
        raise TypeError("note must be a StoreNote")
    kind = exception_kind_for_text(note.text)
    if kind == ExceptionKind.DSD_VENDOR_PULL:
        return dsd_exception_task(note, store_tasks)
    if kind == ExceptionKind.ENDCAP_DISPLAY:
        return endcap_exception_task(note, store_tasks)
    if kind == ExceptionKind.TOPSTOCK:
        return topstock_exception_task(note, store_tasks)
    if kind == ExceptionKind.PICKUP_TOTES:
        return totes_exception_task(note, store_tasks)
    if kind == ExceptionKind.UNCLEAR_LABEL:
        return unclear_label_task(note, store_tasks)
    return planogram_exception_task(note, store_tasks)


def exception_records(notes: list[StoreNote], tasks_by_store: dict[str, list[dict]]) -> list[dict]:
    """Build validated 'exception' plan.jsonl records for all StoreNotes."""
    out: list[dict] = []
    for n in sorted(notes, key=lambda x: (x.store_id, x.note_id)):
        kind = exception_kind_for_text(n.text)
        st_tasks = tasks_by_store.get(n.store_id, [])
        tids = exception_tasks(n, st_tasks)
        payload = {
            "exc_id": make_exc_id(n.store_id, n.note_id, kind),
            "store_id": n.store_id,
            "kind": kind.value,
            "note_id": n.note_id,
            "resolution": resolve_exception(kind),
            "task_ids": tids,
        }
        out.append(record_with_src(payload, "exception", "recallstorm/plan/exceptions_plan.py"))
    return out
