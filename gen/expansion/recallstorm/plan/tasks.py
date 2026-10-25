"""Build PULL, HOLD_VERIFY, PLACE_SUB, and TAG_FLASH shelf tasks for stores."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from contract import (
    Action,
    Allocation,
    Associate,
    Facing,
    SkuDecision,
    Store,
    Verdict,
)
from recallstorm.core.clock import iso_with_offset
from recallstorm.core.ids import make_task_id
from recallstorm.core.jsonl import record_with_src
from recallstorm.store.layout import _aisle_num


@dataclass(frozen=True)
class TaskBuilder:
    """Configures shelf task generation for a store."""

    store: Store
    deadline: datetime


def _loc_dict(facing: Facing) -> dict:
    return {
        "aisle": facing.loc.aisle,
        "bay": facing.loc.bay,
        "shelf": facing.loc.shelf,
        "pos": facing.loc.pos,
    }


def task_window(
    start_dt: datetime,
    duration_mins: int,
    deadline_dt: datetime,
    tz_name: str = "America/Los_Angeles",
) -> list[str]:
    """Compute a [start_iso, end_iso] task window strictly before deadline_dt."""
    safe_end = deadline_dt - timedelta(minutes=5)
    w_start = min(start_dt, safe_end - timedelta(minutes=max(5, duration_mins)))
    w_end = min(safe_end, w_start + timedelta(minutes=max(5, duration_mins)))
    return [iso_with_offset(w_start, tz_name), iso_with_offset(w_end, tz_name)]


def pull_task(
    store_id: str,
    facing: Facing,
    associate_id: str,
    window: list[str],
    seq: int,
    evidence_id: str,
) -> dict:
    """Create a validated PULL shelf_task record."""
    tid = make_task_id(store_id, facing.sku_id, Action.PULL, seq)
    payload = {
        "task_id": tid,
        "store_id": store_id,
        "sku_id": facing.sku_id,
        "action": Action.PULL.value,
        "loc": _loc_dict(facing),
        "qty_units": facing.units,
        "associate_id": associate_id,
        "window": list(window),
        "seq": seq,
        "evidence_id": evidence_id,
        "sub_sku_id": None,
        "alloc_id": None,
    }
    return record_with_src(payload, "shelf_task", "recallstorm/plan/tasks.py")


def hold_verify_task(
    store_id: str,
    facing: Facing,
    associate_id: str,
    window: list[str],
    seq: int,
    evidence_id: str,
) -> dict:
    """Create a validated HOLD_VERIFY shelf_task record."""
    tid = make_task_id(store_id, facing.sku_id, Action.HOLD_VERIFY, seq)
    payload = {
        "task_id": tid,
        "store_id": store_id,
        "sku_id": facing.sku_id,
        "action": Action.HOLD_VERIFY.value,
        "loc": _loc_dict(facing),
        "qty_units": facing.units,
        "associate_id": associate_id,
        "window": list(window),
        "seq": seq,
        "evidence_id": evidence_id,
        "sub_sku_id": None,
        "alloc_id": None,
    }
    return record_with_src(payload, "shelf_task", "recallstorm/plan/tasks.py")


def place_sub_task(
    store_id: str,
    facing: Facing,
    sub_sku_id: str,
    alloc_id: str,
    qty_units: int,
    associate_id: str,
    window: list[str],
    seq: int,
    evidence_id: str,
) -> dict:
    """Create a validated PLACE_SUB shelf_task record."""
    tid = make_task_id(store_id, facing.sku_id, Action.PLACE_SUB, seq)
    payload = {
        "task_id": tid,
        "store_id": store_id,
        "sku_id": facing.sku_id,
        "action": Action.PLACE_SUB.value,
        "loc": _loc_dict(facing),
        "qty_units": qty_units,
        "associate_id": associate_id,
        "window": list(window),
        "seq": seq,
        "evidence_id": evidence_id,
        "sub_sku_id": sub_sku_id,
        "alloc_id": alloc_id,
    }
    return record_with_src(payload, "shelf_task", "recallstorm/plan/tasks.py")


def tag_flash_task(
    store_id: str,
    facing: Facing,
    associate_id: str,
    window: list[str],
    seq: int,
    evidence_id: str,
) -> dict:
    """Create a validated TAG_FLASH shelf_task record."""
    tid = make_task_id(store_id, facing.sku_id, Action.TAG_FLASH, seq)
    payload = {
        "task_id": tid,
        "store_id": store_id,
        "sku_id": facing.sku_id,
        "action": Action.TAG_FLASH.value,
        "loc": _loc_dict(facing),
        "qty_units": 1,
        "associate_id": associate_id,
        "window": list(window),
        "seq": seq,
        "evidence_id": evidence_id,
        "sub_sku_id": None,
        "alloc_id": None,
    }
    return record_with_src(payload, "shelf_task", "recallstorm/plan/tasks.py")


def task_sequence(tasks: list[dict]) -> list[dict]:
    """Re-number task 'seq' fields sequentially starting at 1."""
    out: list[dict] = []
    for idx, t in enumerate(tasks, 1):
        rec = dict(t)
        rec["seq"] = idx
        out.append(rec)
    return out


def task_to_record(task: dict) -> dict:
    """Validate and return a shelf_task record."""
    payload = {k: v for k, v in task.items() if k not in ("type", "src")}
    return record_with_src(payload, "shelf_task", "recallstorm/plan/tasks.py")


def build_shelf_tasks(
    store: Store,
    facings: list[Facing],
    decisions: dict[str, SkuDecision],
    evidence_by_sku: dict[str, dict],
    allocations_by_store_sub: dict[tuple[str, str], Allocation],
    sub_for_pulled: dict[str, str],
    associates: list[Associate],
    deadline: datetime,
) -> list[dict]:
    """Build all PULL, HOLD_VERIFY, PLACE_SUB, and TAG_FLASH tasks for a single store."""
    store_facings = [f for f in facings if f.store_id == store.store_id]
    store_facings.sort(
        key=lambda f: (_aisle_num(f.loc.aisle), f.loc.aisle, f.loc.bay, f.loc.shelf, f.loc.pos, f.sku_id)
    )
    local_assocs = sorted(
        [a for a in associates if a.store_id == store.store_id],
        key=lambda a: a.associate_id,
    )
    if not local_assocs:
        local_assocs = sorted(
            [a for a in associates if a.district == store.district],
            key=lambda a: a.associate_id,
        )
    if not local_assocs and associates:
        local_assocs = [associates[0]]

    base_start = local_assocs[0].shift_start if local_assocs else (deadline - timedelta(hours=8))
    tasks: list[dict] = []
    seq = 0
    used_allocs: set[tuple[str, str]] = set()

    for idx, f in enumerate(store_facings):
        dec = decisions.get(f.sku_id)
        if dec is None or dec.verdict == Verdict.KEEP:
            continue
        ev = evidence_by_sku.get(f.sku_id)
        if not ev:
            continue
        ev_id = ev["evidence_id"]
        assoc = local_assocs[idx % len(local_assocs)] if local_assocs else None
        aid = assoc.associate_id if assoc else f"{store.store_id}-A00"
        t_start = (assoc.shift_start if assoc else base_start) + timedelta(minutes=(seq * 4) % 240)

        if dec.verdict == Verdict.HOLD_VERIFY:
            seq += 1
            win = task_window(t_start, 5, deadline, store.tz)
            tasks.append(hold_verify_task(store.store_id, f, aid, win, seq, ev_id))
            continue

        if dec.verdict == Verdict.PULL:
            seq += 1
            win_pull = task_window(t_start, 5, deadline, store.tz)
            tasks.append(pull_task(store.store_id, f, aid, win_pull, seq, ev_id))

            sub_id = sub_for_pulled.get(f.sku_id)
            alloc = allocations_by_store_sub.get((store.store_id, sub_id)) if sub_id else None
            if alloc is not None and sub_id is not None and (store.store_id, sub_id) not in used_allocs:
                used_allocs.add((store.store_id, sub_id))
                seq += 1
                win_sub = task_window(t_start + timedelta(minutes=6), 6, deadline, store.tz)
                tasks.append(
                    place_sub_task(
                        store.store_id,
                        f,
                        sub_id,
                        alloc.alloc_id,
                        f.units,
                        aid,
                        win_sub,
                        seq,
                        ev_id,
                    )
                )
            else:
                seq += 1
                win_tag = task_window(t_start + timedelta(minutes=6), 3, deadline, store.tz)
                tasks.append(tag_flash_task(store.store_id, f, aid, win_tag, seq, ev_id))

    return tasks
