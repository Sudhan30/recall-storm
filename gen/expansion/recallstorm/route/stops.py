"""Geographic stop ordering, nearest-neighbor routing, and stop merging."""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from contract import RouteManifest, Stop, Store


@dataclass(frozen=True)
class RoutePlanner:
    """Orders stops along a truck route."""

    dc_id: str


def _dist_miles(s1: Store, s2: Store) -> float:
    return math.hypot(s1.lat - s2.lat, s1.lon - s2.lon) * 60.0


def merge_stops(stops: list[Stop] | tuple[Stop, ...]) -> list[Stop]:
    """Combine multiple stops for the same store_id into a single Stop."""
    by_store: dict[str, tuple[int, float, float]] = {}
    for s in stops:
        if s.cases <= 0:
            continue
        prev_c, prev_cu, prev_wt = by_store.get(s.store_id, (0, 0.0, 0.0))
        by_store[s.store_id] = (prev_c + s.cases, prev_cu + s.cube_ft3, prev_wt + s.weight_lb)
    return [
        Stop(store_id=st, cases=c, cube_ft3=round(cu, 2), weight_lb=round(wt, 2))
        for st, (c, cu, wt) in sorted(by_store.items())
    ]


def nearest_neighbor_order(stops: list[Stop], stores_by_id: dict[str, Store] | None = None) -> list[Stop]:
    """Order merged stops using a deterministic nearest-neighbor heuristic starting from the lowest store_id."""
    merged = merge_stops(stops)
    if len(merged) <= 1 or not stores_by_id:
        return merged
    remaining = list(merged)
    ordered: list[Stop] = [remaining.pop(0)]
    while remaining:
        cur_st = stores_by_id.get(ordered[-1].store_id)
        if cur_st is None:
            ordered.append(remaining.pop(0))
            continue
        best_idx = min(
            range(len(remaining)),
            key=lambda i: (
                _dist_miles(cur_st, stores_by_id[remaining[i].store_id])
                if remaining[i].store_id in stores_by_id
                else 9999.0,
                remaining[i].store_id,
            ),
        )
        ordered.append(remaining.pop(best_idx))
    return ordered


def order_stops(stops: list[Stop], stores_by_id: dict[str, Store] | None = None) -> tuple[Stop, ...]:
    """Return a tuple of merged stops ordered for a RouteManifest."""
    return tuple(nearest_neighbor_order(stops, stores_by_id))


def route_distance(stops: list[Stop] | tuple[Stop, ...], stores_by_id: dict[str, Store]) -> float:
    """Compute total inter-stop driving distance in miles."""
    total = 0.0
    for i in range(1, len(stops)):
        s1 = stores_by_id.get(stops[i - 1].store_id)
        s2 = stores_by_id.get(stops[i].store_id)
        if s1 and s2:
            total += _dist_miles(s1, s2)
    return round(total, 2)


def stop_eta(depart: datetime, idx: int) -> datetime:
    """Compute arrival ETA for stop index `idx` (30 minutes per stop)."""
    if idx < 0:
        raise ValueError("idx must be non-negative")
    return depart + timedelta(minutes=30 * (idx + 1))


def stops_for_truck(manifest: RouteManifest) -> tuple[Stop, ...]:
    """Return the stops tuple from a RouteManifest."""
    if not isinstance(manifest, RouteManifest):
        raise TypeError("manifest must be a RouteManifest")
    return manifest.stops


def stop_to_record(stop: Stop) -> dict:
    """Convert a Stop dataclass into a dictionary for route_manifest serialization."""
    return {
        "store_id": stop.store_id,
        "cases": stop.cases,
        "cube_ft3": round(stop.cube_ft3, 2),
        "weight_lb": round(stop.weight_lb, 2),
    }


def stops_summary(stops: list[Stop] | tuple[Stop, ...]) -> dict:
    """Summarize total stops, cases, cube, and weight."""
    return {
        "stop_count": len(stops),
        "total_cases": sum(s.cases for s in stops),
        "total_cube_ft3": round(sum(s.cube_ft3 for s in stops), 2),
        "total_weight_lb": round(sum(s.weight_lb for s in stops), 2),
    }
