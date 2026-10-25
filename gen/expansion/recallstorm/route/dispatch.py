"""Truck departure times, stop arrival ETAs, and DOT driver hour checks."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from contract import RouteManifest, Stop, Store, Truck


@dataclass(frozen=True)
class Dispatcher:
    """Schedules return pickup routes for DC trucks."""

    max_driver_hours: float = 11.0


def depart_time(truck: Truck) -> datetime:
    """Return the scheduled departure datetime of a Truck."""
    if not isinstance(truck, Truck):
        raise TypeError("truck must be a Truck")
    return truck.depart


def arrival_eta(depart: datetime, stop_index: int, distance_miles: float = 20.0) -> datetime:
    """Compute arrival ETA at a stop given departure time, stop sequence index, and distance."""
    if stop_index < 0 or distance_miles < 0:
        raise ValueError("stop_index and distance_miles must be non-negative")
    drive_mins = (distance_miles / 40.0) * 60.0
    dwell_mins = stop_index * 20.0
    return depart + timedelta(minutes=int(round(drive_mins + dwell_mins)))


def driver_hours(stops: list[Stop] | tuple[Stop, ...], distance_miles: float = 50.0) -> float:
    """Estimate total driver duty hours for a route."""
    if distance_miles < 0:
        raise ValueError("distance_miles must be non-negative")
    drive_hrs = distance_miles / 40.0
    loading_hrs = len(stops) * 0.35
    return round(drive_hrs + loading_hrs, 2)


def dispatch_plan(
    manifests: list[RouteManifest],
    trucks_by_id: dict[str, Truck],
    stores_by_id: dict[str, Store] | None = None,
) -> list[dict]:
    """Build a dispatch schedule for each RouteManifest."""
    out: list[dict] = []
    for m in manifests:
        hrs = driver_hours(m.stops, len(m.stops) * 18.0)
        out.append(
            {
                "manifest_id": m.manifest_id,
                "truck_id": m.truck_id,
                "dc_id": m.dc_id,
                "depart": m.depart.isoformat(),
                "stop_count": len(m.stops),
                "driver_hours": hrs,
            }
        )
    return out


def dispatch_to_records(plan: list[dict]) -> list[dict]:
    """Return normalized dispatch records."""
    return [dict(p) for p in plan]


def late_departures(manifests: list[RouteManifest], cutoff: datetime) -> list[str]:
    """Return manifest_ids whose departure is at or after cutoff."""
    return [m.manifest_id for m in manifests if m.depart >= cutoff]


def validate_dispatch(plan: list[dict], max_hours: float = 11.0) -> list[str]:
    """Validate that no route in the dispatch plan exceeds DOT driver hour limits."""
    issues: list[str] = []
    for p in plan:
        if float(p.get("driver_hours", 0.0)) > max_hours:
            issues.append(f"Manifest {p.get('manifest_id')} exceeds driver hours ({p.get('driver_hours')}h)")
    return issues


def dispatch_summary(plan: list[dict]) -> dict:
    """Summarize total dispatches and stops."""
    return {
        "route_count": len(plan),
        "total_stops": sum(int(p.get("stop_count", 0)) for p in plan),
    }
