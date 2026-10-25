"""Build shelf_task records for PULL, HOLD_VERIFY, PLACE_SUB, and TAG_FLASH."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from contract import Action, Allocation, Associate, Facing, Sku, SkuDecision, Store, Verdict
from recallstorm.core.clock import iso_with_offset
from recallstorm.core.ids import make_task_id
from recallstorm.labor.estimates import task_minutes
from recallstorm.labor.shifts import shift_window
from recallstorm.store.layout import aisle_order


@dataclass
class TaskBuilder:
    """Builder for store shelf_task records."""

    store: Store


def _loc_dict(facing: Facing) -> dict:
    return {
        "aisle": facing.loc.aisle,
        "bay": facing.loc.bay,
        "shelf": facing.loc.shelf,
        "pos": facing.loc.pos,
    }


def task_window(start: datetime, duration_mins: float, deadline: datetime) -> list[str]:
    """Return [start_iso, end_iso] clamped strictly before deadline."""
    safe_end = deadline - timedelta(minutes=1)
    end = min(safe_end, start + timedelta(minutes=max(1.0, duration_mins)))
    s = min(start, end - timedelta(minutes=1))
    return [iso_with_offset(s), iso_with_offset(end)]


def pull_task(
    store_id: str,
    facing: Facing,
    evidence_id: str,
    assoc_id: str,
    window: list[str],
    seq: int,
) -> dict:
    """Create a PULL shelf_task record."""
    return {
        "type": "shelf_task",
        "task_id": make_task_id(store_id, facing.sku_id, Action.PULL.value, seq),
        "store_id": store_id,
        "sku_id": facing.sku_id,
        "action": Action.PULL.value,
        "loc": _loc_dict(facing),
        "qty_units": facing.units,
        "associate_id": assoc_id,
        "window": window,
        "seq": seq,
        "evidence_id": evidence_id,
        "sub_sku_id": None,
        "alloc_id": None,
        "src": "recallstorm/plan/tasks.py",
    }


def place_sub_task(
    store_id: str,
    facing: Facing,
    sub_sku_id: str,
    alloc_id: str,
    evidence_id: str,
    assoc_id: str,
    window: list[str],
    seq: int,
    qty_units: int,
) -> dict:
    """Create a PLACE_SUB shelf_task record."""
    return {
        "type": "shelf_task",
        "task_id": make_task_id(store_id, facing.sku_id, Action.PLACE_SUB.value, seq),
        "store_id": store_id,
        "sku_id": facing.sku_id,
        "action": Action.PLACE_SUB.value,
        "loc": _loc_dict(facing),
        "qty_units": qty_units,
        "associate_id": assoc_id,
        "window": window,
        "seq": seq,
        "evidence_id": evidence_id,
        "sub_sku_id": sub_sku_id,
        "alloc_id": alloc_id,
        "src": "recallstorm/plan/tasks.py",
    }


def tag_flash_task(
    store_id: str,
    facing: Facing,
    evidence_id: str,
    assoc_id: str,
    window: list[str],
    seq: int,
) -> dict:
    """Create a TAG_FLASH shelf_task record."""
    return {
        "type": "shelf_task",
        "task_id": make_task_id(store_id, facing.sku_id, Action.TAG_FLASH.value, seq),
        "store_id": store_id,
        "sku_id": facing.sku_id,
        "action": Action.TAG_FLASH.value,
        "loc": _loc_dict(facing),
        "qty_units": 1,
        "associate_id": assoc_id,
        "window": window,
        "seq": seq,
        "evidence_id": evidence_id,
        "sub_sku_id": None,
        "alloc_id": None,
        "src": "recallstorm/plan/tasks.py",
    }


def hold_verify_task(
    store_id: str,
    facing: Facing,
    evidence_id: str,
    assoc_id: str,
    window: list[str],
    seq: int,
) -> dict:
    """Create a HOLD_VERIFY shelf_task record."""
    return {
        "type": "shelf_task",
        "task_id": make_task_id(store_id, facing.sku_id, Action.HOLD_VERIFY.value, seq),
        "store_id": store_id,
        "sku_id": facing.sku_id,
        "action": Action.HOLD_VERIFY.value,
        "loc": _loc_dict(facing),
        "qty_units": facing.units,
        "associate_id": assoc_id,
        "window": window,
        "seq": seq,
        "evidence_id": evidence_id,
        "sub_sku_id": None,
        "alloc_id": None,
        "src": "recallstorm/plan/tasks.py",
    }


def task_sequence(tasks: list[dict]) -> list[dict]:
    """Renumber task 'seq' fields sequentially starting from 1."""
    out: list[dict] = []
    for idx, t in enumerate(tasks, 1):
        r = dict(t)
        r["seq"] = idx
        out.append(r)
    return out


def task_to_record(task: dict) -> dict:
    """Ensure task dictionary has 'type': 'shelf_task' and 'src'."""
    out = dict(task)
    out["type"] = "shelf_task"
    out.setdefault("src", "recallstorm/plan/tasks.py")
    return out


def build_shelf_tasks(
    store: Store,
    facings: list[Facing],
    decisions: dict[str, SkuDecision],
    evidence_by_sku: dict[str, str],
    allocations: list[Allocation],
    skus: dict[str, Sku],
    associates: list[Associate],
    deadline: datetime,
) -> list[dict]:
    """Build all shelf_task records for a store in aisle walk order."""
    st_facings = [f for f in facings if f.store_id == store.store_id]
    ordered_locs = {loc: i for i, loc in enumerate(aisle_order([f.loc for f in st_facings]))}
    st_facings.sort(key=lambda f: (ordered_locs.get(f.loc, 0), f.sku_id))

    st_assocs = [a for a in associates if a.store_id == store.store_id and not a.is_floater]
    if not st_assocs:
        st_assocs = [a for a in associates if a.is_floater and a.district == store.district]
    if not st_assocs and associates:
        st_assocs = [associates[0]]

    # Index allocations available for this store
    store_allocs = [a for a in allocations if a.store_id == store.store_id and a.qty_cases > 0]
    used_alloc_ids: set[str] = set()

    tasks: list[dict] = []
    seq = 1
    if st_assocs:
        base_start, _ = shift_window(st_assocs[0], deadline=deadline)
    else:
        base_start = deadline - timedelta(hours=6)

    cur_time = base_start
    for f in st_facings:
        dec = decisions.get(f.sku_id)
        if not dec or dec.verdict == Verdict.KEEP:
            continue
        ev_id = evidence_by_sku.get(f.sku_id, "")
        assoc_id = st_assocs[(seq - 1) % len(st_assocs)].associate_id if st_assocs else f"{store.store_id}-A00"

        if dec.verdict == Verdict.HOLD_VERIFY:
            dur = task_minutes(Action.HOLD_VERIFY, f.units)
            win = task_window(cur_time, dur, deadline)
            tasks.append(hold_verify_task(store.store_id, f, ev_id, assoc_id, win, seq))
            seq += 1
            cur_time = datetime.fromisoformat(win[1])
        elif dec.verdict == Verdict.PULL:
            dur_p = task_minutes(Action.PULL, f.units)
            win_p = task_window(cur_time, dur_p, deadline)
            tasks.append(pull_task(store.store_id, f, ev_id, assoc_id, win_p, seq))
            seq += 1
            cur_time = datetime.fromisoformat(win_p[1])

            dur_t = task_minutes(Action.TAG_FLASH, 1)
            win_t = task_window(cur_time, dur_t, deadline)
            tasks.append(tag_flash_task(store.store_id, f, ev_id, assoc_id, win_t, seq))
            seq += 1
            cur_time = datetime.fromisoformat(win_t[1])

            # If a substitute allocation exists for this store, place substitute
            avail_alloc = next((a for a in store_allocs if a.alloc_id not in used_alloc_ids), None)
            if avail_alloc is not None:
                used_alloc_ids.add(avail_alloc.alloc_id)
                sub_sku = skus.get(avail_alloc.sub_sku_id)
                sub_units = avail_alloc.qty_cases * (sub_sku.case_units if sub_sku else 12)
                dur_s = task_minutes(Action.PLACE_SUB, sub_units)
                win_s = task_window(cur_time, dur_s, deadline)
                tasks.append(
                    place_sub_task(
                        store.store_id,
                        f,
                        avail_alloc.sub_sku_id,
                        avail_alloc.alloc_id,
                        ev_id,
                        assoc_id,
                        win_s,
                        seq,
                        sub_units,
                    )
                )
                seq += 1
                cur_time = datetime.fromisoformat(win_s[1])

    return tasks
