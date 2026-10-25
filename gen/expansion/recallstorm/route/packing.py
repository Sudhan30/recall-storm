"""Bin-packing of pulled store return cases onto DC trucks implementing pack_returns from contract.py."""
from __future__ import annotations

from dataclasses import dataclass
from contract import RouteManifest, Sku, Stop, Store, Truck
from recallstorm.core.errors import RoutingError
from recallstorm.core.ids import make_manifest_id
from recallstorm.core.jsonl import record_with_src
from recallstorm.route.capacity import capacity_to_record
from recallstorm.route.stops import order_stops, stop_to_record


@dataclass(frozen=True)
class PackingResult:
    """Result of packing store return loads onto trucks."""

    manifests: tuple[RouteManifest, ...]
    total_cases: int


def fits_truck(
    cur_cube: float,
    cur_weight: float,
    add_cube: float,
    add_weight: float,
    max_cube: float,
    max_weight: float,
) -> bool:
    """Return True if adding (add_cube, add_weight) stays within (max_cube, max_weight)."""
    return (cur_cube + add_cube <= max_cube + 1e-6) and (cur_weight + add_weight <= max_weight + 1e-6)


def split_stop(
    store_id: str,
    cases: int,
    unit_cube: float,
    unit_weight: float,
    avail_cube: float,
    avail_weight: float,
) -> tuple[Stop | None, int]:
    """Compute how many integer cases fit in (avail_cube, avail_weight) and return (partial_stop, remaining_cases)."""
    if cases <= 0 or avail_cube <= 0 or avail_weight <= 0:
        return None, max(0, cases)
    by_cube = int(avail_cube // max(1e-6, unit_cube))
    by_wt = int(avail_weight // max(1e-6, unit_weight))
    fit_cases = min(cases, by_cube, by_wt)
    if fit_cases <= 0:
        return None, cases
    stop = Stop(
        store_id=store_id,
        cases=fit_cases,
        cube_ft3=round(fit_cases * unit_cube, 2),
        weight_lb=round(fit_cases * unit_weight, 2),
    )
    return stop, cases - fit_cases


def pack_truck(truck: Truck, items: list[dict]) -> tuple[list[Stop], list[dict]]:
    """Pack store load items onto a single Truck using First-Fit Decreasing without splitting a store across stops."""
    cur_cube = 0.0
    cur_wt = 0.0
    packed: list[Stop] = []
    leftover: list[dict] = []
    for it in items:
        c = int(it["cases"])
        cu = float(it["cube_ft3"])
        wt = float(it["weight_lb"])
        if fits_truck(cur_cube, cur_wt, cu, wt, truck.cube_ft3, truck.weight_lb):
            packed.append(Stop(store_id=str(it["store_id"]), cases=c, cube_ft3=round(cu, 2), weight_lb=round(wt, 2)))
            cur_cube += cu
            cur_wt += wt
        else:
            leftover.append(it)
    return packed, leftover


def first_fit_decreasing(
    items: list[dict],
    trucks: list[Truck],
    stores_by_id: dict[str, Store] | None = None,
) -> list[RouteManifest]:
    """Pack store return items onto DC trucks using First-Fit Decreasing (by cube then store_id)."""
    if not items:
        return []
    if not trucks:
        raise RoutingError("No trucks available to pack return cases")

    ordered_items = sorted(
        [it for it in items if int(it.get("cases", 0)) > 0],
        key=lambda it: (-float(it["cube_ft3"]), -float(it["weight_lb"]), str(it["store_id"])),
    )
    ordered_trucks = sorted(trucks, key=lambda t: t.truck_id)
    bins: list[dict] = [
        {"truck": t, "cube": 0.0, "weight": 0.0, "stops": []}
        for t in ordered_trucks
    ]

    for it in ordered_items:
        placed = False
        cu = float(it["cube_ft3"])
        wt = float(it["weight_lb"])
        st_id = str(it["store_id"])
        cases = int(it["cases"])
        for b in bins:
            tr: Truck = b["truck"]
            if fits_truck(b["cube"], b["weight"], cu, wt, tr.cube_ft3, tr.weight_lb):
                b["stops"].append(Stop(store_id=st_id, cases=cases, cube_ft3=round(cu, 2), weight_lb=round(wt, 2)))
                b["cube"] += cu
                b["weight"] += wt
                placed = True
                break
        if not placed:
            raise RoutingError(f"Store {st_id} return load ({cu} ft3, {wt} lb) exceeds all trucks in DC")

    manifests: list[RouteManifest] = []
    for b in bins:
        if not b["stops"]:
            continue
        tr = b["truck"]
        stops_tuple = order_stops(b["stops"], stores_by_id)
        manifests.append(
            RouteManifest(
                manifest_id=make_manifest_id(tr.truck_id, tr.dc_id),
                truck_id=tr.truck_id,
                dc_id=tr.dc_id,
                stops=stops_tuple,
                depart=tr.depart,
            )
        )
    return manifests


def pack_returns(
    pulled_cases: dict[tuple[str, str], int],
    skus: list[Sku],
    trucks: list[Truck],
    stores: list[Store],
) -> list[RouteManifest]:
    """Pack pulled store return cases onto DC trucks.

    Contract guarantees:
    - Cube and weight on every RouteManifest are strictly within its Truck's limits.
    - Every pulled case in `pulled_cases` appears on exactly one Stop (aggregated per store).
    - Deterministic output order by (dc_id, truck_id).
    """
    if not isinstance(pulled_cases, dict) or not isinstance(skus, list) or not isinstance(trucks, list) or not isinstance(stores, list):
        raise TypeError("Expected pulled_cases dict, skus list, trucks list, and stores list")

    skus_by_id = {s.sku_id: s for s in skus}
    stores_by_id = {s.store_id: s for s in stores}
    trucks_by_dc: dict[str, list[Truck]] = {}
    for t in trucks:
        trucks_by_dc.setdefault(t.dc_id, []).append(t)

    # Aggregate pulled cases, cube, and weight per store_id
    store_totals: dict[str, dict] = {}
    for (store_id, sku_id), cases in sorted(pulled_cases.items()):
        if cases <= 0 or store_id not in stores_by_id:
            continue
        sku = skus_by_id.get(sku_id)
        u_cube = sku.case_cube_ft3 if sku else 1.5
        u_wt = sku.case_weight_lb if sku else 10.0
        entry = store_totals.setdefault(
            store_id,
            {"store_id": store_id, "dc_id": stores_by_id[store_id].dc_id, "cases": 0, "cube_ft3": 0.0, "weight_lb": 0.0},
        )
        entry["cases"] += int(cases)
        entry["cube_ft3"] = round(entry["cube_ft3"] + int(cases) * u_cube, 4)
        entry["weight_lb"] = round(entry["weight_lb"] + int(cases) * u_wt, 4)

    items_by_dc: dict[str, list[dict]] = {}
    for entry in store_totals.values():
        items_by_dc.setdefault(entry["dc_id"], []).append(entry)

    all_manifests: list[RouteManifest] = []
    for dc_id in sorted(items_by_dc.keys()):
        dc_trucks = trucks_by_dc.get(dc_id, [])
        all_manifests.extend(first_fit_decreasing(items_by_dc[dc_id], dc_trucks, stores_by_id))

    return all_manifests


def truck_utilization(manifest: RouteManifest, truck: Truck) -> float:
    """Return max(cube_ratio, weight_ratio) in [0.0, 1.0] for a RouteManifest."""
    c_ratio = sum(s.cube_ft3 for s in manifest.stops) / max(1.0, truck.cube_ft3)
    w_ratio = sum(s.weight_lb for s in manifest.stops) / max(1.0, truck.weight_lb)
    return round(max(c_ratio, w_ratio), 4)


def manifest_to_record(manifest: RouteManifest, truck: Truck) -> dict:
    """Serialize a RouteManifest and its Truck limits into a validated 'route_manifest' plan.jsonl record."""
    payload = {
        "manifest_id": manifest.manifest_id,
        "truck_id": manifest.truck_id,
        "dc_id": manifest.dc_id,
        "stops": [stop_to_record(s) for s in manifest.stops],
        "limits": capacity_to_record(truck),
        "depart": manifest.depart.isoformat(timespec="seconds"),
    }
    return record_with_src(payload, "route_manifest", "recallstorm/route/packing.py")


def packing_summary(manifests: list[RouteManifest]) -> dict:
    """Summarize packed RouteManifests."""
    return {
        "manifest_count": len(manifests),
        "total_stops": sum(len(m.stops) for m in manifests),
        "total_cases": sum(sum(s.cases for s in m.stops) for m in manifests),
    }
