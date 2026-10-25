"""In-store walking path traversal, travel time in seconds, and congestion penalties."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from contract import Location
from recallstorm.store.layout import aisle_order, walking_distance


@dataclass(frozen=True)
class WalkModel:
    """Parameters for associate walking speed and aisle traversal."""

    speed_fps: float = 4.0


def speed_for_associate(is_floater: bool = False) -> float:
    """Return walking speed in feet/second (4.0 fps local, 3.6 fps floater)."""
    return 3.6 if is_floater else 4.0


def congestion_penalty(active_associates: int) -> float:
    """Return a multiplicative travel time penalty >= 1.0 based on active associates in store."""
    if active_associates <= 1:
        return 1.0
    return round(1.0 + 0.05 * (active_associates - 1), 3)


def walk_seconds(loc1: Location, loc2: Location, speed_fps: float = 4.0) -> float:
    """Calculate walking time in seconds between two shelf Locations."""
    if speed_fps <= 0:
        raise ValueError("speed_fps must be positive")
    dist = walking_distance(loc1, loc2)
    return round(dist / speed_fps, 2)


def walk_path(locations: list[Location]) -> list[Location]:
    """Order a list of shelf Locations into an efficient serpentine walk path."""
    return aisle_order(locations)


def aisle_graph(locations: list[Location]) -> dict[str, list[Location]]:
    """Group ordered locations by aisle code."""
    out: dict[str, list[Location]] = {}
    for loc in walk_path(locations):
        out.setdefault(loc.aisle, []).append(loc)
    return out


def shortest_path(loc1: Location, loc2: Location) -> list[Location]:
    """Return the waypoint sequence between loc1 and loc2."""
    if loc1 == loc2:
        return [loc1]
    if loc1.aisle == loc2.aisle:
        return [loc1, loc2]
    alley_waypoint = Location(aisle=loc2.aisle, bay=1, shelf=1, pos=1)
    if alley_waypoint in (loc1, loc2):
        return [loc1, loc2]
    return [loc1, alley_waypoint, loc2]


def path_to_moves(
    path: list[Location],
    store_id: str,
    associate_id: str,
    start_dt: datetime,
    task_id: str,
) -> list[dict]:
    """Convert a Location path into chronological MOVE event dicts."""
    moves: list[dict] = []
    cur_t = start_dt
    prev = path[0] if path else None
    for loc in path:
        if prev is not None and loc != prev:
            secs = max(1, int(walk_seconds(prev, loc)))
            cur_t = cur_t + timedelta(seconds=secs)
        moves.append(
            {
                "t": cur_t.isoformat(timespec="seconds"),
                "store_id": store_id,
                "associate_id": associate_id,
                "kind": "MOVE",
                "loc": {"aisle": loc.aisle, "bay": loc.bay, "shelf": loc.shelf, "pos": loc.pos},
                "task_id": task_id,
            }
        )
        prev = loc
    return moves


def walking_summary(locations: list[Location]) -> dict:
    """Calculate total walking distance in feet along the ordered path of locations."""
    ordered = walk_path(locations)
    total_ft = 0.0
    for i in range(1, len(ordered)):
        total_ft += walking_distance(ordered[i - 1], ordered[i])
    return {"stop_count": len(ordered), "total_distance_ft": round(total_ft, 2)}
