"""Truck cube and weight capacity calculations and overload verification."""
from __future__ import annotations

from dataclasses import dataclass
from contract import RouteManifest, Stop, Truck


@dataclass(frozen=True)
class CapacityModel:
    """Truck capacity limits."""

    cube_ft3: float = 3400.0
    weight_lb: float = 40000.0


def truck_capacity(truck: Truck) -> tuple[float, float]:
    """Return (cube_ft3, weight_lb) limits for a Truck."""
    if not isinstance(truck, Truck):
        raise TypeError("truck must be a Truck")
    return float(truck.cube_ft3), float(truck.weight_lb)


def remaining_cube(truck: Truck, stops: list[Stop] | tuple[Stop, ...]) -> float:
    """Return remaining cubic feet on a truck after loading stops."""
    used = sum(s.cube_ft3 for s in stops)
    return round(truck.cube_ft3 - used, 4)


def remaining_weight(truck: Truck, stops: list[Stop] | tuple[Stop, ...]) -> float:
    """Return remaining weight capacity in pounds on a truck after loading stops."""
    used = sum(s.weight_lb for s in stops)
    return round(truck.weight_lb - used, 4)


def capacity_check(truck: Truck, stops: list[Stop] | tuple[Stop, ...]) -> bool:
    """Return True if total stop cube and weight are within truck limits."""
    total_cube = round(sum(s.cube_ft3 for s in stops), 4)
    total_wt = round(sum(s.weight_lb for s in stops), 4)
    return total_cube <= truck.cube_ft3 + 1e-6 and total_wt <= truck.weight_lb + 1e-6


def overload_report(manifests: list[RouteManifest], trucks_by_id: dict[str, Truck]) -> list[str]:
    """Return a list of overload errors for any manifest exceeding its truck's cube or weight."""
    issues: list[str] = []
    for m in manifests:
        tr = trucks_by_id.get(m.truck_id)
        if tr is None:
            issues.append(f"Manifest {m.manifest_id} references unknown truck {m.truck_id}")
            continue
        if not capacity_check(tr, m.stops):
            issues.append(f"Manifest {m.manifest_id} exceeds capacity of truck {m.truck_id}")
    return issues


def utilization_by_dc(manifests: list[RouteManifest], trucks_by_id: dict[str, Truck]) -> dict[str, float]:
    """Compute max(cube_utilization, weight_utilization) per DC."""
    cube_used: dict[str, float] = {}
    cube_cap: dict[str, float] = {}
    for m in manifests:
        tr = trucks_by_id.get(m.truck_id)
        if tr:
            cube_used[m.dc_id] = cube_used.get(m.dc_id, 0.0) + sum(s.cube_ft3 for s in m.stops)
            cube_cap[m.dc_id] = cube_cap.get(m.dc_id, 0.0) + tr.cube_ft3
    return {
        dc: round(cube_used[dc] / cube_cap[dc], 4) if cube_cap.get(dc, 0.0) > 0 else 0.0
        for dc in sorted(cube_used)
    }


def capacity_to_record(truck: Truck) -> dict[str, float]:
    """Format truck capacity limits for a route_manifest 'limits' field."""
    return {"cube_ft3": round(truck.cube_ft3, 2), "weight_lb": round(truck.weight_lb, 2)}


def capacity_summary(trucks: list[Truck]) -> dict:
    """Summarize fleet capacity."""
    return {
        "truck_count": len(trucks),
        "total_cube_ft3": round(sum(t.cube_ft3 for t in trucks), 2),
        "total_weight_lb": round(sum(t.weight_lb for t in trucks), 2),
    }
