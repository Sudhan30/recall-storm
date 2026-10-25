"""Simulate associate walking paths and travel durations across store aisles."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from contract import Location
from recallstorm.core.clock import iso_with_offset
from recallstorm.store.layout import aisle_order, walking_distance


@dataclass(frozen=True)
class WalkModel:
    """Parameters for associate walking speed and aisle congestion."""

    base_speed_mps: float = 1.2


def speed_for_associate(is_floater: bool = False) -> float:
    """Return walking speed in meters per second."""
    return 1.3 if is_floater else 1.2


def congestion_penalty(associates_in_aisle: int) -> float:
    """Return speed multiplier in (0.0, 1.0] accounting for aisle congestion."""
    if associates_in_aisle <= 1:
        return 1.0
    return round(max(0.5, 1.0 - 0.1 * (associates_in_aisle - 1)), 2)


def walk_seconds(loc1: Location, loc2: Location, speed_mps: float = 1.2) -> float:
    """Compute walking travel time in seconds between two store Locations."""
    if speed_mps <= 0:
        raise ValueError("speed_mps must be positive")
    dist = walking_distance(loc1, loc2)
    return round(dist / speed_mps, 2)


def walk_path(locations: list[Location]) -> list[Location]:
    """Order a list of Locations into a serpentine store walk path."""
    return aisle_order(locations)


def aisle_graph(locations: list[Location]) -> dict[str, list[str]]:
    """Build an adjacency list of aisles present in locations."""
    aisles = sorted({l.aisle for l in locations})
    graph: dict[str, list[str]] = {a: [] for a in aisles}
    for i in range(len(aisles) - 1):
        graph[aisles[i]].append(aisles[i + 1])
        graph[aisles[i + 1]].append(aisles[i])
    return graph


def shortest_path(loc1: Location, loc2: Location) -> list[Location]:
    """Return the waypoint path from loc1 to loc2."""
    if loc1 == loc2:
        return [loc1]
    return [loc1, loc2]


def path_to_moves(
    store_id: str,
    assoc_id: str,
    task_id: str,
    path: list[Location],
    start_t: datetime,
) -> list[dict]:
    """Convert a sequence of Locations into discrete MOVE event dictionaries."""
    out: list[dict] = []
    cur_t = start_t
    for idx, loc in enumerate(path):
        if idx > 0:
            sec = walk_seconds(path[idx - 1], loc)
            cur_t = cur_t + timedelta(seconds=max(1.0, sec))
        out.append(
            {
                "t": iso_with_offset(cur_t),
                "store_id": store_id,
                "associate_id": assoc_id,
                "kind": "MOVE",
                "loc": {"aisle": loc.aisle, "bay": loc.bay, "shelf": loc.shelf, "pos": loc.pos},
                "task_id": task_id,
            }
        )
    return out


def walking_summary(locations: list[Location]) -> dict:
    """Compute total walking distance and seconds along the ordered walk path."""
    ordered = walk_path(locations)
    total_dist = 0.0
    total_sec = 0.0
    for i in range(1, len(ordered)):
        total_dist += walking_distance(ordered[i - 1], ordered[i])
        total_sec += walk_seconds(ordered[i - 1], ordered[i])
    return {
        "stops": len(ordered),
        "total_distance_m": round(total_dist, 2),
        "total_seconds": round(total_sec, 2),
    }
