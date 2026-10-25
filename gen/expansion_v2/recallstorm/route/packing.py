"""First-fit-decreasing return packing implementing pack_returns from contract.py."""
from __future__ import annotations

from dataclasses import dataclass, field
import math

from contract import RouteManifest, Sku, Stop, Store, Truck
from recallstorm.core.clock import iso_with_offset
from recallstorm.core.errors import RoutingError
from recallstorm.core.ids import make_manifest_id
from recallstorm.route.capacity import capacity_to_record
from recallstorm.route.stops import order_stops, stop_to_record


@dataclass
class PackingResult:
    """Container for packed RouteManifests."""

    manifests: list[RouteManifest] = field(default_factory=list)


def fits_truck(
    truck: Truck,
    current_cube: float,
    current_weight: float,
    add_cube: float,
    add_weight: float,
) -> bool:
    """Return True if adding (add_cube, add_weight) stays within truck.cube_ft3 and truck.weight_lb."""
    return (current_cube + add_cube <= truck.cube_ft3 + 1e-6) and (
        current_weight + add_weight <= truck.weight_lb + 1e-6
    )


def split_stop(
    store_id: str,
    cases: int,
    unit_cube: float,
    unit_weight: float,
    max_cube: float,
    max_weight: float,
) -> tuple[Stop | None, int]:
    """Fit as many integer cases as possible within (max_cube, max_weight); return (Stop_or_None, remaining_cases)."""
    if cases <= 0 or max_cube <= 0 or max_weight <= 0:
        return (None, max(0, cases))
    by_cube = int(math.floor((max_cube + 1e-9) / unit_cube)) if unit_cube > 0 else cases
    by_weight = int(math.floor((max_weight + 1e-9) / unit_weight)) if unit_weight > 0 else cases
    fit_cases = min(cases, by_cube, by_weight)
    if fit_cases <= 0:
        return (None, cases)
    stop = Stop(
        store_id=store_id,
        cases=fit_cases,
        cube_ft3=round(fit_cases * unit_cube, 4),
        weight_lb=round(fit_cases * unit_weight, 4),
    )
    return (stop, cases - fit_cases)


def pack_truck(
    truck: Truck, items: list[tuple[str, int, float, float]]
) -> tuple[list[Stop], list[tuple[str, int, float, float]]]:
    """Pack store return items (store_id, cases, cube, weight) onto a single truck; return (loaded_stops, leftover_items)."""
    loaded: list[Stop] = []
    leftover: list[tuple[str, int, float, float]] = []
    cur_c = 0.0
    cur_w = 0.0

    for st_id, cases, tot_c, tot_w in items:
        if cases <= 0:
            continue
        if fits_truck(truck, cur_c, cur_w, tot_c, tot_w):
            loaded.append(Stop(st_id, cases, round(tot_c, 4), round(tot_w, 4)))
            cur_c += tot_c
            cur_w += tot_w
        else:
            unit_c = tot_c / cases
            unit_w = tot_w / cases
            part_stop, rem_cases = split_stop(
                st_id,
                cases,
                unit_c,
                unit_w,
                max(0.0, truck.cube_ft3 - cur_c),
                max(0.0, truck.weight_lb - cur_w),
            )
            if part_stop is not None:
                loaded.append(part_stop)
                cur_c += part_stop.cube_ft3
                cur_w += part_stop.weight_lb
            if rem_cases > 0:
                leftover.append((st_id, rem_cases, round(rem_cases * unit_c, 4), round(rem_cases * unit_w, 4)))
    return (loaded, leftover)


def first_fit_decreasing(
    items: list[tuple[str, int, float, float]], trucks: list[Truck]
) -> dict[str, list[Stop]]:
    """Pack items onto trucks using First-Fit Decreasing (sorted by cube descending, tie-break by store_id)."""
    ordered_items = sorted(items, key=lambda x: (-x[2], -x[3], x[0]))
    ordered_trucks = sorted(trucks, key=lambda t: t.truck_id)
    by_truck: dict[str, list[Stop]] = {}
    pending = ordered_items
    for trk in ordered_trucks:
        if not pending:
            break
        loaded, pending = pack_truck(trk, pending)
        if loaded:
            by_truck[trk.truck_id] = loaded
    if pending:
        raise RoutingError(f"Insufficient truck capacity to pack remaining cases: {pending}")
    return by_truck


def pack_returns(
    pulled_cases: dict[tuple[str, str], int],
    skus: list[Sku],
    trucks: list[Truck],
    stores: list[Store],
) -> list[RouteManifest]:
    """Pack pulled store return cases onto DC trucks.

    Implements the contract.py signature and invariants:
      - Cube and weight on every RouteManifest are within its Truck limits
      - Every pulled case is placed on a stop (conservation of returned cases)
      - Deterministic ordering by dc_id, truck_id, and store_id
    """
    if not pulled_cases or not trucks or not stores:
        return []

    sku_map = {s.sku_id: s for s in skus}
    store_map = {s.store_id: s for s in stores}
    trucks_by_dc: dict[str, list[Truck]] = {}
    for t in sorted(trucks, key=lambda x: x.truck_id):
        trucks_by_dc.setdefault(t.dc_id, []).append(t)

    # Aggregate (store_id, sku_id) -> cases into per-DC store loads: (store_id, cases, cube, weight)
    dc_store_totals: dict[str, dict[str, list[float]]] = {}
    for (store_id, sku_id), raw_cases in sorted(pulled_cases.items()):
        cases = int(raw_cases)
        if cases <= 0 or store_id not in store_map:
            continue
        st = store_map[store_id]
        sku = sku_map.get(sku_id)
        c_ft3 = cases * (sku.case_cube_ft3 if sku else 1.5)
        w_lb = cases * (sku.case_weight_lb if sku else 10.0)
        dc_bucket = dc_store_totals.setdefault(st.dc_id, {})
        acc = dc_bucket.setdefault(store_id, [0.0, 0.0, 0.0])
        acc[0] += cases
        acc[1] += c_ft3
        acc[2] += w_lb

    manifests: list[RouteManifest] = []
    for dc_id in sorted(dc_store_totals.keys()):
        dc_trucks = trucks_by_dc.get(dc_id, [])
        if not dc_trucks:
            continue
        items: list[tuple[str, int, float, float]] = [
            (st_id, int(vals[0]), round(vals[1], 4), round(vals[2], 4))
            for st_id, vals in sorted(dc_store_totals[dc_id].items())
            if int(vals[0]) > 0
        ]
        packed_by_truck = first_fit_decreasing(items, dc_trucks)
        trk_lookup = {t.truck_id: t for t in dc_trucks}
        for seq, (tid, stops_list) in enumerate(sorted(packed_by_truck.items())):
            trk = trk_lookup[tid]
            ordered = order_stops(stops_list, store_map)
            manifests.append(
                RouteManifest(
                    manifest_id=make_manifest_id(tid, seq),
                    truck_id=tid,
                    dc_id=dc_id,
                    stops=ordered,
                    depart=trk.depart,
                )
            )
    return manifests


def truck_utilization(manifest: RouteManifest, truck: Truck) -> dict[str, float]:
    """Compute cube and weight utilization ratios in [0.0, 1.0] for manifest on truck."""
    tot_c = sum(s.cube_ft3 for s in manifest.stops)
    tot_w = sum(s.weight_lb for s in manifest.stops)
    return {
        "cube_ratio": round(tot_c / truck.cube_ft3, 4) if truck.cube_ft3 > 0 else 0.0,
        "weight_ratio": round(tot_w / truck.weight_lb, 4) if truck.weight_lb > 0 else 0.0,
    }


def manifest_to_record(manifest: RouteManifest, truck: Truck) -> dict:
    """Serialize a RouteManifest and Truck to a plan.jsonl 'route_manifest' record."""
    return {
        "type": "route_manifest",
        "manifest_id": manifest.manifest_id,
        "truck_id": manifest.truck_id,
        "dc_id": manifest.dc_id,
        "stops": [stop_to_record(s) for s in manifest.stops],
        "limits": capacity_to_record(truck),
        "depart": iso_with_offset(manifest.depart),
        "src": "recallstorm/route/packing.py",
    }


def packing_summary(manifests: list[RouteManifest]) -> dict:
    """Summarize packed manifests, total stops, and total cases."""
    return {
        "manifest_count": len(manifests),
        "total_stops": sum(len(m.stops) for m in manifests),
        "total_cases": sum(sum(s.cases for s in m.stops) for m in manifests),
    }
