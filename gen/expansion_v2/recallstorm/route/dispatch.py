"""Truck dispatch planning, depart times, ETAs, and DOT driver hours."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from contract import RouteManifest, Truck
from recallstorm.core.clock import is_before_deadline, iso_with_offset
from recallstorm.route.capacity import capacity_to_record
from recallstorm.route.stops import stop_to_record


@dataclass
class Dispatcher:
    """Fleet dispatcher for return route manifests."""

    trucks: dict[str, Truck]


def depart_time(truck: Truck) -> datetime:
    """Return the scheduled departure datetime for truck."""
    return truck.depart


def arrival_eta(depart: datetime, num_stops: int) -> datetime:
    """Estimate truck return arrival back at DC after num_stops."""
    return depart + timedelta(minutes=max(1, num_stops) * 35 + 30)


def driver_hours(num_stops: int, distance_km: float = 50.0) -> float:
    """Estimate total DOT driver duty hours for a route."""
    if num_stops < 0 or distance_km < 0:
        raise ValueError("Negative stops or distance_km")
    drive_hrs = distance_km / 65.0
    stop_hrs = num_stops * 0.4
    return round(drive_hrs + stop_hrs, 2)


def dispatch_plan(manifests: list[RouteManifest], trucks: dict[str, Truck]) -> list[dict]:
    """Create a dispatch schedule for manifests."""
    out: list[dict] = []
    for m in manifests:
        out.append(
            {
                "manifest_id": m.manifest_id,
                "truck_id": m.truck_id,
                "dc_id": m.dc_id,
                "depart": iso_with_offset(m.depart),
                "eta": iso_with_offset(arrival_eta(m.depart, len(m.stops))),
                "driver_hours": driver_hours(len(m.stops)),
            }
        )
    return out


def dispatch_to_records(manifests: list[RouteManifest], trucks: dict[str, Truck]) -> list[dict]:
    """Convert RouteManifests into plan.jsonl 'route_manifest' records."""
    out: list[dict] = []
    for m in manifests:
        t = trucks.get(m.truck_id)
        limits = capacity_to_record(t) if t else {"cube_ft3": 3400.0, "weight_lb": 40000.0}
        out.append(
            {
                "type": "route_manifest",
                "manifest_id": m.manifest_id,
                "truck_id": m.truck_id,
                "dc_id": m.dc_id,
                "stops": [stop_to_record(s) for s in m.stops],
                "limits": limits,
                "depart": iso_with_offset(m.depart),
                "src": "recallstorm/route/dispatch.py",
            }
        )
    return out


def late_departures(manifests: list[RouteManifest], cutoff: datetime) -> list[str]:
    """Return manifest_ids whose depart time is at or after cutoff."""
    return [m.manifest_id for m in manifests if not is_before_deadline(m.depart, cutoff, strict=True)]


def validate_dispatch(manifests: list[RouteManifest], trucks: dict[str, Truck]) -> list[str]:
    """Validate that all manifests reference valid trucks and stay within DOT 11-hour driving limits."""
    issues: list[str] = []
    for m in manifests:
        if m.truck_id not in trucks:
            issues.append(f"Manifest {m.manifest_id} references unknown truck {m.truck_id}")
        if driver_hours(len(m.stops)) > 11.0:
            issues.append(f"Manifest {m.manifest_id} exceeds DOT driver hours")
    return issues


def dispatch_summary(manifests: list[RouteManifest]) -> dict:
    """Summarize dispatched manifests."""
    return {
        "manifest_count": len(manifests),
        "total_stops": sum(len(m.stops) for m in manifests),
    }
