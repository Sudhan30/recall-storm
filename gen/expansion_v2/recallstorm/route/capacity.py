"""Truck cube and weight capacity checks and utilization summaries."""
from __future__ import annotations

from dataclasses import dataclass

from contract import RouteManifest, Stop, Truck


@dataclass(frozen=True)
class CapacityModel:
    """Truck capacity model."""

    default_cube_ft3: float = 3400.0
    default_weight_lb: float = 40000.0


def truck_capacity(truck: Truck) -> tuple[float, float]:
    """Return (cube_ft3, weight_lb) capacity limits for truck."""
    return (float(truck.cube_ft3), float(truck.weight_lb))


def remaining_cube(truck: Truck, stops: list[Stop] | tuple[Stop, ...]) -> float:
    """Return remaining cubic feet on truck after loading stops."""
    used = sum(float(s.cube_ft3) for s in stops)
    return round(float(truck.cube_ft3) - used, 4)


def remaining_weight(truck: Truck, stops: list[Stop] | tuple[Stop, ...]) -> float:
    """Return remaining weight in pounds on truck after loading stops."""
    used = sum(float(s.weight_lb) for s in stops)
    return round(float(truck.weight_lb) - used, 4)


def capacity_check(truck: Truck, stops: list[Stop] | tuple[Stop, ...]) -> bool:
    """Return True if total cube and total weight of stops are within truck's limits."""
    return remaining_cube(truck, stops) >= -1e-6 and remaining_weight(truck, stops) >= -1e-6


def overload_report(manifests: list[RouteManifest], trucks: dict[str, Truck]) -> list[str]:
    """Return diagnostic strings for any RouteManifest exceeding its truck capacity."""
    issues: list[str] = []
    for m in manifests:
        t = trucks.get(m.truck_id)
        if t and not capacity_check(t, m.stops):
            issues.append(f"Manifest {m.manifest_id} overloads truck {m.truck_id}")
    return issues


def utilization_by_dc(manifests: list[RouteManifest], trucks: dict[str, Truck]) -> dict[str, dict]:
    """Compute aggregate cube and weight utilization by dc_id."""
    out: dict[str, dict] = {}
    for m in manifests:
        b = out.setdefault(m.dc_id, {"manifests": 0, "cube_ft3": 0.0, "weight_lb": 0.0})
        b["manifests"] += 1
        b["cube_ft3"] = round(b["cube_ft3"] + sum(s.cube_ft3 for s in m.stops), 2)
        b["weight_lb"] = round(b["weight_lb"] + sum(s.weight_lb for s in m.stops), 2)
    return out


def capacity_to_record(truck: Truck) -> dict:
    """Return limits dictionary {'cube_ft3': ..., 'weight_lb': ...} for route_manifest records."""
    return {"cube_ft3": float(truck.cube_ft3), "weight_lb": float(truck.weight_lb)}


def capacity_summary(manifests: list[RouteManifest], trucks: list[Truck]) -> dict:
    """Summarize fleet capacity and manifest overloads."""
    t_map = {t.truck_id: t for t in trucks}
    over = overload_report(manifests, t_map)
    return {
        "manifest_count": len(manifests),
        "truck_count": len(trucks),
        "overload_count": len(over),
    }
