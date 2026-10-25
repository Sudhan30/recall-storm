"""Deterministic return-truck bin packing per distribution center."""
from __future__ import annotations

from dataclasses import dataclass, field
from contract import RouteManifest, Sku, Stop, Store, Truck

_EPS = 1e-9
_SRC = "recallstorm/route/packer.py"


@dataclass
class _StoreLoad:
    store_id: str
    dc_id: str
    sku_cases: list[tuple[Sku, int]]

    @property
    def total_cases(self) -> int:
        return sum(qty for _, qty in self.sku_cases)

    @property
    def total_cube(self) -> float:
        return round(sum(sku.case_cube_ft3 * qty for sku, qty in self.sku_cases), 6)

    @property
    def total_weight(self) -> float:
        return round(sum(sku.case_weight_lb * qty for sku, qty in self.sku_cases), 6)


@dataclass
class _StopAccumulator:
    store_id: str
    cases: int = 0
    cube_ft3: float = 0.0
    weight_lb: float = 0.0

    def add_cases(self, sku: Sku, count: int) -> None:
        self.cases += count
        self.cube_ft3 = round(self.cube_ft3 + sku.case_cube_ft3 * count, 6)
        self.weight_lb = round(self.weight_lb + sku.case_weight_lb * count, 6)

    def to_stop(self) -> Stop:
        return Stop(
            store_id=self.store_id,
            cases=self.cases,
            cube_ft3=round(self.cube_ft3, 6),
            weight_lb=round(self.weight_lb, 6),
        )


@dataclass
class _TruckBin:
    truck: Truck
    stops_by_store: dict[str, _StopAccumulator] = field(default_factory=dict)
    used_cube: float = 0.0
    used_weight: float = 0.0

    @property
    def rem_cube(self) -> float:
        return self.truck.cube_ft3 - self.used_cube

    @property
    def rem_weight(self) -> float:
        return self.truck.weight_lb - self.used_weight

    def can_fit(self, cube: float, weight: float) -> bool:
        return (self.used_cube + cube <= self.truck.cube_ft3 + _EPS) and (
            self.used_weight + weight <= self.truck.weight_lb + _EPS
        )

    def max_cases_that_fit(self, sku: Sku, max_wanted: int) -> int:
        if max_wanted <= 0:
            return 0
        fit_by_cube = max_wanted
        if sku.case_cube_ft3 > 0:
            fit_by_cube = int((self.rem_cube + _EPS) // sku.case_cube_ft3)
        fit_by_weight = max_wanted
        if sku.case_weight_lb > 0:
            fit_by_weight = int((self.rem_weight + _EPS) // sku.case_weight_lb)
        candidate = max(0, min(max_wanted, fit_by_cube, fit_by_weight))
        while candidate > 0 and not self.can_fit(
            round(sku.case_cube_ft3 * candidate, 6),
            round(sku.case_weight_lb * candidate, 6),
        ):
            candidate -= 1
        return candidate

    def add_sku_cases(self, store_id: str, sku: Sku, count: int) -> None:
        if count <= 0:
            return
        acc = self.stops_by_store.get(store_id)
        if acc is None:
            acc = _StopAccumulator(store_id=store_id)
            self.stops_by_store[store_id] = acc
        acc.add_cases(sku, count)
        self.used_cube = round(sum(s.cube_ft3 for s in self.stops_by_store.values()), 6)
        self.used_weight = round(sum(s.weight_lb for s in self.stops_by_store.values()), 6)


def _try_pack_whole_stores(
    loads: list[_StoreLoad], dc_trucks: list[Truck]
) -> list[_TruckBin] | None:
    """Attempt to pack each store's load without splitting across trucks."""
    bins: list[_TruckBin] = []
    next_truck_idx = 0

    for load in loads:
        cube = load.total_cube
        weight = load.total_weight
        placed = False
        for b in bins:
            if b.can_fit(cube, weight):
                for sku, qty in load.sku_cases:
                    b.add_sku_cases(load.store_id, sku, qty)
                placed = True
                break
        if not placed:
            while next_truck_idx < len(dc_trucks):
                candidate_bin = _TruckBin(truck=dc_trucks[next_truck_idx])
                next_truck_idx += 1
                if candidate_bin.can_fit(cube, weight):
                    for sku, qty in load.sku_cases:
                        candidate_bin.add_sku_cases(load.store_id, sku, qty)
                    bins.append(candidate_bin)
                    placed = True
                    break
            if not placed:
                return None
    return [b for b in bins if b.stops_by_store]


def _pack_with_splitting(
    dc_id: str, loads: list[_StoreLoad], dc_trucks: list[Truck]
) -> list[_TruckBin]:
    """Pack store loads into DC trucks, splitting across trucks only when a store load cannot fit whole."""
    bins: list[_TruckBin] = []
    next_truck_idx = 0

    for load in loads:
        cube = load.total_cube
        weight = load.total_weight

        # First check if the entire store load fits into an already-open truck.
        placed_whole = False
        for b in bins:
            if b.can_fit(cube, weight):
                for sku, qty in load.sku_cases:
                    b.add_sku_cases(load.store_id, sku, qty)
                placed_whole = True
                break
        if placed_whole:
            continue

        # Otherwise split across open trucks and open new trucks as needed.
        for sku, qty in load.sku_cases:
            remaining = qty
            if sku.case_cube_ft3 < 0 or sku.case_weight_lb < 0:
                raise ValueError(f"SKU {sku.sku_id} has negative cube or weight")

            for b in bins:
                if remaining == 0:
                    break
                take = b.max_cases_that_fit(sku, remaining)
                if take > 0:
                    b.add_sku_cases(load.store_id, sku, take)
                    remaining -= take

            while remaining > 0:
                if next_truck_idx >= len(dc_trucks):
                    raise ValueError(
                        f"DC {dc_id} lacks truck capacity for returns "
                        f"(unable to pack {remaining} cases of {sku.sku_id} for store {load.store_id})"
                    )
                new_bin = _TruckBin(truck=dc_trucks[next_truck_idx])
                next_truck_idx += 1
                take = new_bin.max_cases_that_fit(sku, remaining)
                if take <= 0:
                    continue
                new_bin.add_sku_cases(load.store_id, sku, take)
                bins.append(new_bin)
                remaining -= take

    return [b for b in bins if b.stops_by_store]


def pack_returns(
    pulled_cases: dict[tuple[str, str], int],
    skus: list[Sku],
    trucks: list[Truck],
    stores: list[Store],
) -> list[RouteManifest]:
    """Pack pulled store return cases onto DC trucks within cube and weight limits."""
    if not pulled_cases:
        return []

    sku_by_id: dict[str, Sku] = {s.sku_id: s for s in skus}
    store_by_id: dict[str, Store] = {st.store_id: st for st in stores}

    # Group valid positive pulled_cases by store_id
    by_store: dict[str, dict[str, int]] = {}
    for (store_id, sku_id), cases in sorted(pulled_cases.items()):
        if cases < 0:
            raise ValueError(f"Negative pulled cases ({cases}) for ({store_id}, {sku_id})")
        if cases == 0:
            continue
        if store_id not in store_by_id:
            raise ValueError(f"Unknown store_id in pulled_cases: {store_id}")
        if sku_id not in sku_by_id:
            raise ValueError(f"Unknown sku_id in pulled_cases: {sku_id}")
        by_store.setdefault(store_id, {})
        by_store[store_id][sku_id] = by_store[store_id].get(sku_id, 0) + int(cases)

    if not by_store:
        return []

    # Group store loads by DC
    loads_by_dc: dict[str, list[_StoreLoad]] = {}
    for store_id in sorted(by_store.keys()):
        store = store_by_id[store_id]
        sku_qty_map = by_store[store_id]
        sku_cases = [(sku_by_id[sku_id], sku_qty_map[sku_id]) for sku_id in sorted(sku_qty_map.keys())]
        loads_by_dc.setdefault(store.dc_id, []).append(
            _StoreLoad(store_id=store_id, dc_id=store.dc_id, sku_cases=sku_cases)
        )

    # Group trucks by DC in deterministic order (depart, truck_id), deduplicating truck_id
    trucks_by_dc: dict[str, list[Truck]] = {}
    seen_truck_ids: set[str] = set()
    for truck in sorted(trucks, key=lambda t: (t.dc_id, t.depart, t.truck_id)):
        if truck.truck_id in seen_truck_ids:
            raise ValueError(f"Duplicate truck_id in trucks input: {truck.truck_id}")
        seen_truck_ids.add(truck.truck_id)
        trucks_by_dc.setdefault(truck.dc_id, []).append(truck)

    manifests: list[RouteManifest] = []
    for dc_id in sorted(loads_by_dc.keys()):
        dc_loads = loads_by_dc[dc_id]
        dc_trucks = trucks_by_dc.get(dc_id, [])
        if not dc_trucks:
            raise ValueError(f"DC {dc_id} has no available trucks for return loads")

        total_dc_cube = sum(ld.total_cube for ld in dc_loads)
        total_dc_weight = sum(ld.total_weight for ld in dc_loads)
        cap_dc_cube = sum(t.cube_ft3 for t in dc_trucks)
        cap_dc_weight = sum(t.weight_lb for t in dc_trucks)
        if total_dc_cube > cap_dc_cube + _EPS or total_dc_weight > cap_dc_weight + _EPS:
            raise ValueError(
                f"DC {dc_id} lacks total capacity for returns: "
                f"needs ({total_dc_cube:.2f} ft3, {total_dc_weight:.2f} lb), "
                f"available ({cap_dc_cube:.2f} ft3, {cap_dc_weight:.2f} lb)"
            )

        # Prefer packing whole stores without splitting when possible
        packed_bins = _try_pack_whole_stores(dc_loads, dc_trucks)
        if packed_bins is None:
            packed_bins = _pack_with_splitting(dc_id, dc_loads, dc_trucks)

        for idx, b in enumerate(packed_bins):
            stops = tuple(
                b.stops_by_store[sid].to_stop() for sid in sorted(b.stops_by_store.keys())
            )
            manifest_id = f"M-{dc_id}-{idx:03d}"
            manifests.append(
                RouteManifest(
                    manifest_id=manifest_id,
                    truck_id=b.truck.truck_id,
                    dc_id=dc_id,
                    stops=stops,
                    depart=b.truck.depart,
                )
            )

    return manifests


def manifest_to_plan_record(manifest: RouteManifest, truck: Truck) -> dict[str, object]:
    """Serialize a RouteManifest into the plan.jsonl route_manifest schema."""
    return {
        "type": "route_manifest",
        "manifest_id": manifest.manifest_id,
        "truck_id": manifest.truck_id,
        "dc_id": manifest.dc_id,
        "stops": [
            {
                "store_id": s.store_id,
                "cases": s.cases,
                "cube_ft3": s.cube_ft3,
                "weight_lb": s.weight_lb,
            }
            for s in manifest.stops
        ],
        "limits": {
            "cube_ft3": truck.cube_ft3,
            "weight_lb": truck.weight_lb,
        },
        "depart": manifest.depart.isoformat(),
        "src": _SRC,
    }
