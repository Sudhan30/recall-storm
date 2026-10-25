"""Quarantine surge slotting, seasonal aisle conversion, and dock reservations."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class QuarantineSlottingPlanner:
    """Planner allocating surge quarantine space in a distribution center."""

    ref_id: str = "SLT-PLN-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class SurgeCapacityAllocator:
    """Allocator converting bulk floor/seasonal bays into return staging."""

    ref_id: str = "SLT-SRG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def calculate_cubic_feet_needed_for_recall_hold(cases: int, case_cube_ft3: float,expansion_factor: float = 1.25) -> float:
    """Calculate DC quarantine space in cubic feet including pallet/aisle expansion_factor."""
    if cases < 0 or case_cube_ft3 <= 0 or expansion_factor < 1.0:
        raise DataValidationError("Invalid cube calculation inputs")
    return round(cases * case_cube_ft3 * expansion_factor, 2)


def convert_bulk_floor_stack_to_quarantine_zone(dc_id: str, bay_ids: list[str]) -> dict:
    """Convert bulk floor-stack bays into a temporary roped-off recall quarantine zone."""
    _req(dc_id, "dc_id")
    if not bay_ids:
        raise DataValidationError("bay_ids cannot be empty")
    return {"op": "convert_bulk_floor_stack_to_quarantine_zone", "dc_id": str(dc_id), "bays": sorted(bay_ids), "src": "recallstorm/dc_ops/slotting_adjustments.py"}


def re_slot_seasonal_aisle_for_return_staging(dc_id: str, aisle: str) -> dict:
    """Re-slot a flex/seasonal DC aisle for inbound store recall returns."""
    _req(dc_id, "dc_id")
    _req(aisle, "aisle")
    return {"op": "re_slot_seasonal_aisle_for_return_staging", "dc_id": str(dc_id), "aisle": str(aisle), "src": "recallstorm/dc_ops/slotting_adjustments.py"}


def isolate_allergen_or_chemical_leaker_racks(rack_id: str) -> dict:
    """Assign bottom-level floor positions with spill trays for leaking chemical or allergen holds."""
    _req(rack_id, "rack_id")
    return {"op": "isolate_allergen_or_chemical_leaker_racks", "rack_id": str(rack_id), "floor_level_only": True, "src": "recallstorm/dc_ops/slotting_adjustments.py"}


def optimize_forklift_travel_to_compactor_bay(staging_bays: dict[str, float]) -> str:
    """Select the staging bay with shortest travel distance to the compactor."""
    if not staging_bays:
        raise DataValidationError("staging_bays cannot be empty")
    return min(staging_bays.items(), key=lambda x: (float(x[1]), str(x[0])))[0]


def reserve_dock_doors_for_reverse_consolidation(dc_id: str, doors: list[int]) -> dict:
    """Reserve dedicated dock doors for unloading store recall return trucks."""
    _req(dc_id, "dc_id")
    if not doors or any(d <= 0 for d in doors):
        raise DataValidationError("Invalid dock doors")
    return {"op": "reserve_dock_doors_for_reverse_consolidation", "dc_id": str(dc_id), "doors": sorted(doors), "src": "recallstorm/dc_ops/slotting_adjustments.py"}


def balance_freezer_vs_ambient_hold_capacity(freezer_pallets: int, ambient_pallets: int, max_freezer: int = 50) -> dict:
    """Check whether freezer quarantine pallets fit within DC cold-room hold capacity."""
    if freezer_pallets < 0 or ambient_pallets < 0 or max_freezer <= 0:
        raise DataValidationError("Invalid pallet counts")
    return {"op": "balance_freezer_vs_ambient_hold_capacity", "reefer_trailer_needed": freezer_pallets > max_freezer, "src": "recallstorm/dc_ops/slotting_adjustments.py"}


def update_wms_zone_velocity_restrictions(zone_id: str, velocity_code: str = "HOLD") -> dict:
    """Set WMS slotting velocity code to 'HOLD' so auto-slotting ignores the quarantine zone."""
    _req(zone_id, "zone_id")
    return {"op": "update_wms_zone_velocity_restrictions", "zone_id": str(zone_id), "velocity_code": str(velocity_code), "src": "recallstorm/dc_ops/slotting_adjustments.py"}


def track_temporary_rack_reconfiguration_cost(labor_hours: float, rate_usd: float = 35.0) -> float:
    """Calculate DC slotting reconfiguration labor cost."""
    if labor_hours < 0 or rate_usd < 0:
        raise DataValidationError("Negative labor cost inputs")
    return round(float(labor_hours) * float(rate_usd), 2)


def restore_baseline_slotting_post_disposition(dc_id: str, zone_id: str) -> dict:
    """Restore temporary quarantine bays to active reserve slotting after recall disposition."""
    _req(dc_id, "dc_id")
    _req(zone_id, "zone_id")
    return {"op": "restore_baseline_slotting_post_disposition", "dc_id": str(dc_id), "zone_id": str(zone_id), "restored": True, "src": "recallstorm/dc_ops/slotting_adjustments.py"}
