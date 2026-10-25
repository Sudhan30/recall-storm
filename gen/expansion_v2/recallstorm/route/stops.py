"""Order truck stops deterministically using nearest-neighbor and store_id."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import math

from contract import RouteManifest, Stop, Store


@dataclass
class RoutePlanner:
    """Stop ordering and distance calculator."""

    stores: dict[str, Store]


def merge_stops(stops: list[Stop]) -> list[Stop]:
    """Merge stops visiting the same store_id on the same truck."""
    by_store: dict[str, Stop] = {}
    for s in stops:
        if s.cases <= 0:
            continue
        if s.store_id in by_store:
            prev = by_store[s.store_id]
            by_store[s.store_id] = Stop(
                store_id=s.store_id,
                cases=prev.cases + s.cases,
                cube_ft3=round(prev.cube_ft3 + s.cube_ft3, 4),
                weight_lb=round(prev.weight_lb + s.weight_lb, 4),
            )
        else:
            by_store[s.store_id] = s
    return [by_store[k] for k in sorted(by_store.keys())]


def nearest_neighbor_order(stops: list[Stop], stores: dict[str, Store]) -> list[Stop]:
    """Order merged stops using deterministic nearest-neighbor starting from lowest store_id."""
    merged = merge_stops(stops)
    if len(merged) <= 1 or not stores:
        return merged
    remaining = list(merged)
    remaining.sort(key=lambda s: s.store_id)
    ordered: list[Stop] = [remaining.pop(0)]
    while remaining:
        cur_st = stores.get(ordered[-1].store_id)
        if not cur_st:
            ordered.extend(remaining)
            break

        def _dist_key(cand: Stop) -> tuple[float, str]:
            st2 = stores.get(cand.store_id)
            if not st2:
                return (999999.0, cand.store_id)
            d = math.hypot(cur_st.lat - st2.lat, cur_st.lon - st2.lon)
            return (round(d, 6), cand.store_id)

        nxt = min(remaining, key=_dist_key)
        remaining.remove(nxt)
        ordered.append(nxt)
    return ordered


def order_stops(stops: list[Stop], stores: dict[str, Store] | None = None) -> tuple[Stop, ...]:
    """Merge and deterministically order stops for a RouteManifest."""
    if stores:
        return tuple(nearest_neighbor_order(stops, stores))
    return tuple(merge_stops(stops))


def route_distance(stops: list[Stop] | tuple[Stop, ...], stores: dict[str, Store]) -> float:
    """Compute approximate route distance in kilometers across stops."""
    if len(stops) <= 1:
        return 0.0
    total_km = 0.0
    for i in range(1, len(stops)):
        s1 = stores.get(stops[i - 1].store_id)
        s2 = stores.get(stops[i].store_id)
        if s1 and s2:
            total_km += math.hypot(s1.lat - s2.lat, s1.lon - s2.lon) * 111.0
    return round(total_km, 2)


def stop_eta(depart: datetime, stop_index: int, mins_per_stop: int = 30) -> datetime:
    """Estimate arrival datetime at stop_index (0-based)."""
    if stop_index < 0 or mins_per_stop <= 0:
        raise ValueError("Invalid stop_index or mins_per_stop")
    return depart + timedelta(minutes=(stop_index + 1) * mins_per_stop)


def stops_for_truck(manifest: RouteManifest) -> tuple[Stop, ...]:
    """Return the tuple of Stops on manifest."""
    return manifest.stops


def stop_to_record(stop: Stop) -> dict:
    """Serialize a Stop dataclass to a dictionary."""
    return {
        "store_id": stop.store_id,
        "cases": stop.cases,
        "cube_ft3": round(stop.cube_ft3, 4),
        "weight_lb": round(stop.weight_lb, 4),
    }


def stops_summary(stops: list[Stop] | tuple[Stop, ...]) -> dict:
    """Summarize stop count, total cases, cube, and weight."""
    return {
        "stop_count": len(stops),
        "total_cases": sum(s.cases for s in stops),
        "total_cube_ft3": round(sum(s.cube_ft3 for s in stops), 2),
        "total_weight_lb": round(sum(s.weight_lb for s in stops), 2),
    }
