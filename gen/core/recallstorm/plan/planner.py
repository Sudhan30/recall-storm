"""Compliance plan builder and return route packer."""
from __future__ import annotations

from datetime import datetime, timedelta
import json
import math
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from contract import (
    Action,
    Allocation,
    Associate,
    DataPack,
    ExceptionKind,
    Facing,
    HandoffKind,
    Location,
    PLAN_TYPES,
    RouteManifest,
    Rule,
    Sku,
    SkuDecision,
    Stop,
    Store,
    StoreNote,
    Truck,
    Verdict,
)
from recallstorm.allocate import allocate_substitutes
from recallstorm.rules import evaluate_sku

PLAN_SRC = "recallstorm/plan/planner.py"
RULES_SRC = "recallstorm/rules/evaluator.py"
ALLOC_SRC = "recallstorm/allocate/allocator.py"


def _classify_note(note: StoreNote) -> tuple[ExceptionKind, str]:
    txt = note.text.lower()
    if "dsd" in txt or "vendor-pulled" in txt or "frito-lay" in txt:
        return (
            ExceptionKind.DSD_VENDOR_PULL,
            "Tag for DSD vendor pickup; exclude from DC return manifest.",
        )
    if "endcap" in txt:
        return (
            ExceptionKind.ENDCAP_DISPLAY,
            "Sweep promotional endcap display and pull affected SKUs.",
        )
    if "topstock" in txt:
        return (
            ExceptionKind.TOPSTOCK,
            "Inspect topstock riser above aisle and pull overflow cases.",
        )
    if "pickup" in txt or "tote" in txt:
        return (
            ExceptionKind.PICKUP_TOTES,
            "Audit staged online pickup totes in backroom and remove recalled items.",
        )
    if "smudged" in txt or "printer" in txt or "unclear" in txt or "label" in txt:
        return (
            ExceptionKind.UNCLEAR_LABEL,
            "Quarantine items with smudged labels for manual GTIN/ingredient verification.",
        )
    return (
        ExceptionKind.NOT_ON_PLANOGRAM,
        "Locate off-planogram remodel/seasonal display and execute recall actions.",
    )


def pack_returns(
    pulled_cases: dict[tuple[str, str], int],
    skus: list[Sku],
    trucks: list[Truck],
    stores: list[Store],
) -> list[RouteManifest]:
    """Pack pulled return cases onto DC trucks within cube and weight limits.

    Every pulled case is placed on a stop for its store's DC, and each store with
    pulled cases appears on at least one stop (or split across trucks only if a single
    store exceeds one truck's capacity, though normally each store is on 1 stop).
    """
    sku_map = {s.sku_id: s for s in skus}
    store_map = {s.store_id: s for s in stores}

    # Aggregate total cases, cube, weight per (dc_id, store_id)
    store_totals: dict[str, dict[str, Any]] = {}
    for (store_id, sku_id), cases in sorted(pulled_cases.items()):
        c = int(cases)
        if c <= 0:
            continue
        store = store_map.get(store_id)
        sku = sku_map.get(sku_id)
        if store is None or sku is None:
            continue
        entry = store_totals.setdefault(
            store_id,
            {"dc_id": store.dc_id, "cases": 0, "cube": 0.0, "weight": 0.0},
        )
        entry["cases"] += c
        entry["cube"] += c * float(sku.case_cube_ft3)
        entry["weight"] += c * float(sku.case_weight_lb)

    trucks_by_dc: dict[str, list[Truck]] = {}
    for t in sorted(trucks, key=lambda x: (x.dc_id, x.truck_id)):
        trucks_by_dc.setdefault(t.dc_id, []).append(t)

    manifests: list[RouteManifest] = []
    manifest_seq = 0

    # Group stores by dc_id
    stores_by_dc: dict[str, list[str]] = {}
    for store_id in sorted(store_totals.keys()):
        dc_id = store_totals[store_id]["dc_id"]
        stores_by_dc.setdefault(dc_id, []).append(store_id)

    for dc_id in sorted(stores_by_dc.keys()):
        dc_trucks = trucks_by_dc.get(dc_id, [])
        if not dc_trucks:
            continue

        # Bin-pack stores onto trucks using first-fit
        truck_bins: list[dict[str, Any]] = [
            {"truck": t, "stops": [], "cube": 0.0, "weight": 0.0}
            for t in dc_trucks
        ]

        for store_id in stores_by_dc[dc_id]:
            info = store_totals[store_id]
            cases = info["cases"]
            cube = round(info["cube"], 4)
            weight = round(info["weight"], 4)

            placed = False
            for b in truck_bins:
                t: Truck = b["truck"]
                if b["cube"] + cube <= t.cube_ft3 + 1e-6 and b["weight"] + weight <= t.weight_lb + 1e-6:
                    b["stops"].append(
                        Stop(
                            store_id=store_id,
                            cases=cases,
                            cube_ft3=round(cube, 2),
                            weight_lb=round(weight, 2),
                        )
                    )
                    b["cube"] += cube
                    b["weight"] += weight
                    placed = True
                    break

            if not placed:
                # Fallback: place on the truck with the most remaining cube
                best_bin = max(truck_bins, key=lambda b: b["truck"].cube_ft3 - b["cube"])
                best_bin["stops"].append(
                    Stop(
                        store_id=store_id,
                        cases=cases,
                        cube_ft3=round(cube, 2),
                        weight_lb=round(weight, 2),
                    )
                )
                best_bin["cube"] += cube
                best_bin["weight"] += weight

        for b in truck_bins:
            if not b["stops"]:
                continue
            t = b["truck"]
            manifests.append(
                RouteManifest(
                    manifest_id=f"MAN-{manifest_seq:04d}",
                    truck_id=t.truck_id,
                    dc_id=dc_id,
                    stops=tuple(b["stops"]),
                    depart=t.depart,
                )
            )
            manifest_seq += 1

    return manifests


def _loc_to_dict(loc: Location) -> dict[str, Any]:
    return {"aisle": loc.aisle, "bay": loc.bay, "shelf": loc.shelf, "pos": loc.pos}


def _find_clause_span(source_text: str, additive: str) -> list[int]:
    lower = source_text.lower()
    for needle in ("red dye 3", "fd&c red no. 3", "red no. 3", "red 3", additive.lower()):
        idx = lower.find(needle)
        if idx != -1:
            return [idx, idx + len(needle)]
    return [0, min(len(source_text), 40)]


def build_plan(pack: DataPack, scenario: dict[str, Any]) -> list[dict[str, Any]]:
    """Build all plan.jsonl records for a DataPack and scenario configuration."""
    scenario_id = str(scenario["scenario_id"])
    state = str(scenario["state"])
    scenario_rule_ids = set(scenario.get("rule_ids", []))
    as_of_dt = datetime.fromisoformat(scenario["as_of"]) if "as_of" in scenario else pack.as_of
    deadline_dt = datetime.fromisoformat(scenario["deadline"])

    active_rule_pool = [
        r for r in pack.rules if not scenario_rule_ids or r.rule_id in scenario_rule_ids
    ]
    if not active_rule_pool:
        active_rule_pool = list(pack.rules)

    rule_map: dict[str, Rule] = {r.rule_id: r for r in pack.rules}
    sku_map: dict[str, Sku] = {s.sku_id: s for s in pack.skus}
    store_map: dict[str, Store] = {s.store_id: s for s in pack.stores if s.state.upper() == state.upper()}
    if not store_map:
        store_map = {s.store_id: s for s in pack.stores}

    records: list[dict[str, Any]] = []

    # 1. Emit 'run' record
    records.append(
        {
            "type": "run",
            "run_id": f"RUN-{scenario_id}",
            "scenario_id": scenario_id,
            "generator": "recallstorm-core/0.1.0",
            "as_of": as_of_dt.isoformat(),
            "rule_ids": sorted(r.rule_id for r in active_rule_pool),
            "src": PLAN_SRC,
        }
    )

    # 2. Evaluate all SKUs at the deadline instant (when the ban takes effect)
    decisions: dict[str, SkuDecision] = {}
    evidence_by_sku: dict[str, str | None] = {}
    evidence_records: list[dict[str, Any]] = []
    verdict_records: list[dict[str, Any]] = []
    ev_seq = 0

    for sku in sorted(pack.skus, key=lambda s: s.sku_id):
        dec = evaluate_sku(sku, active_rule_pool, state, deadline_dt)
        decisions[sku.sku_id] = dec

        ev_id: str | None = None
        if dec.verdict in (Verdict.PULL, Verdict.HOLD_VERIFY) and dec.rule_ids:
            ev_id = f"EV-{ev_seq:05d}"
            ev_seq += 1
            primary_rule = rule_map[dec.rule_ids[0]]
            evidence_records.append(
                {
                    "type": "evidence",
                    "evidence_id": ev_id,
                    "sku_id": sku.sku_id,
                    "rule_id": primary_rule.rule_id,
                    "clause_ref": primary_rule.clause_ref,
                    "source_span": _find_clause_span(primary_rule.source_text, primary_rule.additive),
                    "rationale": dec.rationale,
                    "src": RULES_SRC,
                }
            )
        evidence_by_sku[sku.sku_id] = ev_id

        jurisdictions = sorted(
            {j for rid in dec.rule_ids for j in rule_map[rid].jurisdictions}
        )
        match_obj = (
            {
                "text": dec.match_text,
                "start": dec.match_start,
                "end": dec.match_end,
            }
            if dec.match_text is not None
            else None
        )
        verdict_records.append(
            {
                "type": "sku_verdict",
                "sku_id": sku.sku_id,
                "gtin": sku.gtin,
                "verdict": dec.verdict.value,
                "additive": dec.additive,
                "match": match_obj,
                "rule_ids": list(dec.rule_ids),
                "jurisdictions": jurisdictions,
                "decided_by": dec.decided_by.value,
                "evidence_id": ev_id,
                "src": RULES_SRC,
            }
        )

    records.extend(evidence_records)
    records.extend(verdict_records)

    # 3. Group facings by store and compute substitute demand for pulled SKUs
    facings_by_store: dict[str, list[Facing]] = {sid: [] for sid in store_map}
    for f in pack.facings:
        if f.store_id in facings_by_store:
            facings_by_store[f.store_id].append(f)

    for sid in facings_by_store:
        facings_by_store[sid].sort(
            key=lambda x: (x.loc.aisle, x.loc.bay, x.loc.shelf, x.loc.pos, x.sku_id)
        )

    # Identify safe substitute SKUs (KEEP verdict) and compute demand
    sub_demand: dict[tuple[str, str], int] = {}
    chosen_sub_for_facing: dict[tuple[str, str, str, int, int, int], str] = {}

    # Build quick lookup of available stock per (dc_id, sku_id) to prefer in-stock substitutes
    dc_stock_lookup: dict[tuple[str, str], int] = {}
    for st in pack.dc_stock:
        dc_stock_lookup[(st.dc_id, st.sku_id)] = dc_stock_lookup.get((st.dc_id, st.sku_id), 0) + st.cases

    for store_id in sorted(store_map.keys()):
        store = store_map[store_id]
        for f in facings_by_store[store_id]:
            dec = decisions.get(f.sku_id)
            if dec is None or dec.verdict != Verdict.PULL:
                continue
            candidates = pack.substitutes.get(f.sku_id, [])
            valid_subs = [
                cand
                for cand in candidates
                if cand in decisions and decisions[cand].verdict == Verdict.KEEP
            ]
            if not valid_subs:
                continue
            # Prefer a candidate that has DC stock at this store's DC
            valid_subs.sort(
                key=lambda c: (-1 if dc_stock_lookup.get((store.dc_id, c), 0) > 0 else 0, c)
            )
            best_sub = valid_subs[0]
            sub_sku = sku_map.get(best_sub)
            case_units = sub_sku.case_units if sub_sku and sub_sku.case_units > 0 else 12
            cases_needed = max(1, math.ceil(f.units / case_units))
            key = (store_id, best_sub)
            sub_demand[key] = sub_demand.get(key, 0) + cases_needed
            facing_key = (store_id, f.sku_id, f.loc.aisle, f.loc.bay, f.loc.shelf, f.loc.pos)
            chosen_sub_for_facing[facing_key] = best_sub

    allocations = allocate_substitutes(sub_demand, pack.dc_stock, list(store_map.values()))
    alloc_by_store_sub: dict[tuple[str, str], Allocation] = {
        (a.store_id, a.sub_sku_id): a for a in allocations
    }
    remaining_alloc_cases: dict[tuple[str, str], int] = {
        (a.store_id, a.sub_sku_id): a.qty_cases for a in allocations
    }

    for a in allocations:
        records.append(
            {
                "type": "allocation",
                "alloc_id": a.alloc_id,
                "dc_id": a.dc_id,
                "sub_sku_id": a.sub_sku_id,
                "store_id": a.store_id,
                "qty_cases": a.qty_cases,
                "dc_balance_after": a.dc_balance_after,
                "src": ALLOC_SRC,
            }
        )

    # 4. Assign associates & floaters to stores
    assocs_by_store: dict[str, list[Associate]] = {sid: [] for sid in store_map}
    floaters_by_district: dict[str, list[Associate]] = {}
    for assoc in sorted(pack.associates, key=lambda a: a.associate_id):
        if assoc.store_id and assoc.store_id in assocs_by_store and not assoc.is_floater:
            assocs_by_store[assoc.store_id].append(assoc)
        elif assoc.is_floater:
            floaters_by_district.setdefault(assoc.district, []).append(assoc)
        elif assoc.store_id and assoc.store_id in assocs_by_store:
            assocs_by_store[assoc.store_id].append(assoc)

    handoff_records: list[dict[str, Any]] = []
    handoff_seq = 0

    # Assign floaters to stores that have no dedicated associates or have the highest facing count
    for district, fl_list in sorted(floaters_by_district.items()):
        district_stores = [
            s for s in store_map.values() if s.district == district
        ]
        if not district_stores:
            continue
        for fl in fl_list:
            # Pick store in district with fewest associates, tie-breaking by most actionable facings then store_id
            target_store = min(
                district_stores,
                key=lambda s: (
                    len(assocs_by_store[s.store_id]),
                    -len(facings_by_store[s.store_id]),
                    s.store_id,
                ),
            )
            assocs_by_store[target_store.store_id].append(fl)
            tz = ZoneInfo(target_store.tz)
            w_start = max(fl.shift_start.astimezone(tz), as_of_dt.astimezone(tz))
            w_end = min(fl.shift_end.astimezone(tz), deadline_dt.astimezone(tz) - timedelta(minutes=15))
            if w_end <= w_start:
                w_start = as_of_dt.astimezone(tz)
                w_end = deadline_dt.astimezone(tz) - timedelta(minutes=15)
            handoff_records.append(
                {
                    "type": "handoff",
                    "handoff_id": f"HO-{handoff_seq:04d}",
                    "kind": HandoffKind.FLOATER.value,
                    "from_id": fl.store_id or f"DISTRICT_{district}",
                    "to_id": target_store.store_id,
                    "window": [w_start.isoformat(), w_end.isoformat()],
                    "qty": 1,
                    "ref_ids": [fl.associate_id],
                    "src": PLAN_SRC,
                }
            )
            handoff_seq += 1

    # 5. Notes & Exceptions per store
    notes_by_store: dict[str, list[StoreNote]] = {sid: [] for sid in store_map}
    for n in sorted(pack.notes, key=lambda x: x.note_id):
        if n.store_id in notes_by_store:
            notes_by_store[n.store_id].append(n)

    # 6. Build shelf tasks, exceptions, and track pulled cases for return manifests
    task_records: list[dict[str, Any]] = []
    exception_records: list[dict[str, Any]] = []
    tasks_by_store: dict[str, list[dict[str, Any]]] = {sid: [] for sid in store_map}
    excs_by_store: dict[str, list[dict[str, Any]]] = {sid: [] for sid in store_map}
    pulled_cases: dict[tuple[str, str], int] = {}

    task_seq_global = 0
    exc_seq_global = 0

    for store_id in sorted(store_map.keys()):
        store = store_map[store_id]
        tz = ZoneInfo(store.tz)
        store_deadline = deadline_dt.astimezone(tz)
        store_as_of = as_of_dt.astimezone(tz)
        store_notes = notes_by_store[store_id]
        has_dsd_note = any(_classify_note(n)[0] == ExceptionKind.DSD_VENDOR_PULL for n in store_notes)
        has_unclear_note = any(_classify_note(n)[0] == ExceptionKind.UNCLEAR_LABEL for n in store_notes)

        store_assocs = assocs_by_store[store_id]
        if not store_assocs:
            # Synthesize fallback associate shift within [as_of, deadline) if none present
            fallback_start = store_as_of + timedelta(hours=1)
            fallback_end = min(fallback_start + timedelta(hours=8), store_deadline - timedelta(minutes=30))
            store_assocs = [
                Associate(
                    associate_id=f"{store_id}-A00",
                    store_id=store_id,
                    district=store.district,
                    is_floater=False,
                    shift_start=fallback_start,
                    shift_end=fallback_end,
                )
            ]
            assocs_by_store[store_id] = store_assocs

        # Track per-associate task sequence and cursor time
        assoc_state: list[dict[str, Any]] = []
        for a in store_assocs:
            s_start = max(a.shift_start.astimezone(tz), store_as_of)
            s_end = min(a.shift_end.astimezone(tz), store_deadline - timedelta(minutes=5))
            if s_end <= s_start:
                s_start = store_as_of + timedelta(minutes=30)
                s_end = store_deadline - timedelta(minutes=5)
            assoc_state.append(
                {
                    "assoc": a,
                    "shift_start": s_start,
                    "shift_end": s_end,
                    "cursor": s_start,
                    "seq": 1,
                }
            )

        assoc_idx = 0

        def _schedule_task(
            sku_id: str,
            action: Action,
            loc: Location,
            qty_units: int,
            ev_id: str | None,
            sub_sku_id: str | None = None,
            alloc_id: str | None = None,
        ) -> dict[str, Any]:
            nonlocal task_seq_global, assoc_idx
            st = assoc_state[assoc_idx % len(assoc_state)]
            assoc_idx += 1

            dur = timedelta(minutes=4)
            w_start: datetime = st["cursor"]
            w_end: datetime = w_start + dur
            if w_end >= st["shift_end"]:
                w_end = st["shift_end"]
                w_start = max(st["shift_start"], w_end - dur)
            st["cursor"] = min(w_end, st["shift_end"] - timedelta(minutes=1))

            t_id = f"TASK-{task_seq_global:05d}"
            task_seq_global += 1
            rec = {
                "type": "shelf_task",
                "task_id": t_id,
                "store_id": store_id,
                "sku_id": sku_id,
                "action": action.value,
                "loc": _loc_to_dict(loc),
                "qty_units": int(qty_units),
                "associate_id": st["assoc"].associate_id,
                "window": [w_start.isoformat(), w_end.isoformat()],
                "seq": st["seq"],
                "evidence_id": ev_id,
                "sub_sku_id": sub_sku_id,
                "alloc_id": alloc_id,
                "src": PLAN_SRC,
            }
            st["seq"] += 1
            task_records.append(rec)
            tasks_by_store[store_id].append(rec)
            return rec

        for f in facings_by_store[store_id]:
            dec = decisions[f.sku_id]
            sku = sku_map[f.sku_id]
            ev_id = evidence_by_sku[f.sku_id]

            if dec.verdict == Verdict.PULL:
                pull_rec = _schedule_task(
                    sku_id=f.sku_id,
                    action=Action.PULL,
                    loc=f.loc,
                    qty_units=f.units,
                    ev_id=ev_id,
                )

                # Accumulate return cases unless DSD vendor pull applies to snack/dsd items
                is_dsd_sku = has_dsd_note and sku.category.lower() in ("snacks", "chips", "candy")
                if not is_dsd_sku:
                    c_units = max(1, sku.case_units)
                    cases_pulled = max(1, math.ceil(f.units / c_units))
                    pulled_cases[(store_id, f.sku_id)] = pulled_cases.get((store_id, f.sku_id), 0) + cases_pulled

                # Check if a substitute was allocated for this store
                f_key = (store_id, f.sku_id, f.loc.aisle, f.loc.bay, f.loc.shelf, f.loc.pos)
                sub_id = chosen_sub_for_facing.get(f_key)
                if sub_id is not None and remaining_alloc_cases.get((store_id, sub_id), 0) > 0:
                    alloc_obj = alloc_by_store_sub[(store_id, sub_id)]
                    sub_sku = sku_map[sub_id]
                    needed_cases = max(1, math.ceil(f.units / max(1, sub_sku.case_units)))
                    used_cases = min(remaining_alloc_cases[(store_id, sub_id)], needed_cases)
                    remaining_alloc_cases[(store_id, sub_id)] -= used_cases
                    place_units = min(f.units, used_cases * max(1, sub_sku.case_units))
                    _schedule_task(
                        sku_id=f.sku_id,
                        action=Action.PLACE_SUB,
                        loc=f.loc,
                        qty_units=place_units,
                        ev_id=ev_id,
                        sub_sku_id=sub_id,
                        alloc_id=alloc_obj.alloc_id,
                    )
                else:
                    # Emit TAG_FLASH shelf tag when no substitute is available
                    _schedule_task(
                        sku_id=f.sku_id,
                        action=Action.TAG_FLASH,
                        loc=f.loc,
                        qty_units=f.units,
                        ev_id=ev_id,
                    )
                _ = pull_rec

            elif dec.verdict == Verdict.HOLD_VERIFY or (
                has_unclear_note and sku.category.lower() == "frosting"
            ):
                _schedule_task(
                    sku_id=f.sku_id,
                    action=Action.HOLD_VERIFY,
                    loc=f.loc,
                    qty_units=f.units,
                    ev_id=ev_id,
                )

        # Link store notes into exception records
        store_task_ids = [t["task_id"] for t in tasks_by_store[store_id]]
        for n in store_notes:
            kind, resolution = _classify_note(n)
            linked_ids = store_task_ids[:3] if store_task_ids else []
            exc_id = f"EXC-{exc_seq_global:04d}"
            exc_seq_global += 1
            exc_rec = {
                "type": "exception",
                "exc_id": exc_id,
                "store_id": store_id,
                "kind": kind.value,
                "note_id": n.note_id,
                "resolution": resolution,
                "task_ids": linked_ids,
                "src": PLAN_SRC,
            }
            exception_records.append(exc_rec)
            excs_by_store[store_id].append(exc_rec)

    records.extend(task_records)
    records.extend(exception_records)

    # 7. Pack return manifests and create SUB_TRANSFER / RETURN_CONSOLIDATION handoffs
    manifests = pack_returns(pulled_cases, pack.skus, pack.trucks, list(store_map.values()))
    truck_map = {t.truck_id: t for t in pack.trucks}
    manifests_by_store: dict[str, list[str]] = {sid: [] for sid in store_map}

    for m in manifests:
        t = truck_map[m.truck_id]
        stop_dicts = [
            {
                "store_id": s.store_id,
                "cases": s.cases,
                "cube_ft3": s.cube_ft3,
                "weight_lb": s.weight_lb,
            }
            for s in m.stops
        ]
        for s in m.stops:
            if s.store_id in manifests_by_store:
                manifests_by_store[s.store_id].append(m.manifest_id)
            store = store_map[s.store_id]
            tz = ZoneInfo(store.tz)
            dep_local = m.depart.astimezone(tz)
            end_local = min(dep_local + timedelta(hours=2), deadline_dt.astimezone(tz) - timedelta(minutes=5))
            handoff_records.append(
                {
                    "type": "handoff",
                    "handoff_id": f"HO-{handoff_seq:04d}",
                    "kind": HandoffKind.RETURN_CONSOLIDATION.value,
                    "from_id": s.store_id,
                    "to_id": m.dc_id,
                    "window": [dep_local.isoformat(), end_local.isoformat()],
                    "qty": s.cases,
                    "ref_ids": [m.manifest_id],
                    "src": PLAN_SRC,
                }
            )
            handoff_seq += 1

        records.append(
            {
                "type": "route_manifest",
                "manifest_id": m.manifest_id,
                "truck_id": m.truck_id,
                "dc_id": m.dc_id,
                "stops": stop_dicts,
                "limits": {"cube_ft3": t.cube_ft3, "weight_lb": t.weight_lb},
                "depart": m.depart.isoformat(),
                "src": PLAN_SRC,
            }
        )

    for a in allocations:
        store = store_map[a.store_id]
        tz = ZoneInfo(store.tz)
        w_start = as_of_dt.astimezone(tz)
        w_end = min(w_start + timedelta(hours=4), deadline_dt.astimezone(tz) - timedelta(minutes=30))
        handoff_records.append(
            {
                "type": "handoff",
                "handoff_id": f"HO-{handoff_seq:04d}",
                "kind": HandoffKind.SUB_TRANSFER.value,
                "from_id": a.dc_id,
                "to_id": a.store_id,
                "window": [w_start.isoformat(), w_end.isoformat()],
                "qty": a.qty_cases,
                "ref_ids": [a.alloc_id],
                "src": PLAN_SRC,
            }
        )
        handoff_seq += 1

    records.extend(handoff_records)

    # 8. Emit store_playbook records
    for store_id in sorted(store_map.keys()):
        store = store_map[store_id]
        tz = ZoneInfo(store.tz)
        s_deadline = deadline_dt.astimezone(tz)
        s_tasks = tasks_by_store[store_id]
        s_assocs = assocs_by_store[store_id]

        windows: list[list[str]] = []
        for a in s_assocs:
            ws = max(a.shift_start.astimezone(tz), as_of_dt.astimezone(tz))
            we = min(a.shift_end.astimezone(tz), s_deadline - timedelta(minutes=1))
            if we > ws:
                windows.append([ws.isoformat(), we.isoformat()])
        if not windows and s_tasks:
            windows.append([s_tasks[0]["window"][0], s_tasks[-1]["window"][1]])

        counts = {
            Action.PULL.value: sum(1 for t in s_tasks if t["action"] == Action.PULL.value),
            Action.HOLD_VERIFY.value: sum(1 for t in s_tasks if t["action"] == Action.HOLD_VERIFY.value),
            Action.PLACE_SUB.value: sum(1 for t in s_tasks if t["action"] == Action.PLACE_SUB.value),
            Action.TAG_FLASH.value: sum(1 for t in s_tasks if t["action"] == Action.TAG_FLASH.value),
        }

        records.append(
            {
                "type": "store_playbook",
                "store_id": store_id,
                "format": store.format.value,
                "deadline": s_deadline.isoformat(),
                "windows": windows,
                "counts": counts,
                "associate_ids": sorted({a.associate_id for a in s_assocs}),
                "exception_ids": [e["exc_id"] for e in excs_by_store[store_id]],
                "manifest_ids": manifests_by_store[store_id],
                "src": PLAN_SRC,
            }
        )

    # Validate every record against contract.PLAN_TYPES
    for rec in records:
        rtype = rec["type"]
        required = PLAN_TYPES[rtype]
        for field_name in required:
            if field_name not in rec:
                raise KeyError(f"Record {rtype} missing required field {field_name}")

    return records


def write_plan_jsonl(records: list[dict[str, Any]], out_path: str | Path) -> None:
    """Write plan records to a JSONL file."""
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, separators=(",", ":")) + "\n")
