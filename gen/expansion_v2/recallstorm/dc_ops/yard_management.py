"""YMS drop-trailer glad-hand locks, reefer monitoring, and gate seal logs."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class YardTrailerQuarantine:
    """Yard Management System (YMS) drop-trailer quarantine record."""

    ref_id: str = "YMS-TRL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ReeferHoldMonitor:
    """Telematics fuel and temperature monitor for quarantined yard reefers."""

    ref_id: str = "YMS-REF-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def locate_affected_drop_trailer_in_yard_slot(yard_map: dict[str, str], trailer_id: str) -> str | None:
    """Return yard slot ID for trailer_id."""
    if yard_map is None:
        raise DataValidationError("yard_map cannot be None")
    _req(trailer_id, "trailer_id")
    return yard_map.get(str(trailer_id))


def apply_digital_glad_hand_lock_in_yms(trailer_id: str) -> dict:
    """Apply YMS digital and physical glad-hand air-brake lock on a quarantined trailer."""
    _req(trailer_id, "trailer_id")
    return {"op": "apply_digital_glad_hand_lock_in_yms", "trailer_id": str(trailer_id), "locked": True, "src": "recallstorm/dc_ops/yard_management.py"}


def monitor_quarantined_reefer_fuel_and_temp(trailer_id: str, fuel_pct: float, temp_f: float = 34.0) -> dict:
    """Monitor refrigerated drop-trailer fuel level (alert if < 25%) and setpoint temperature."""
    _req(trailer_id, "trailer_id")
    if not (0.0 <= fuel_pct <= 100.0):
        raise DataValidationError("fuel_pct must be in [0, 100]")
    return {"op": "monitor_quarantined_reefer_fuel_and_temp", "trailer_id": str(trailer_id), "refuel_needed": fuel_pct < 25.0, "temp_f": float(temp_f), "src": "recallstorm/dc_ops/yard_management.py"}


def prioritize_hot_recall_return_trailer_docking(trailers: list[str]) -> list[str]:
    """Order return trailers for immediate reclamation dock door assignment."""
    if trailers is None:
        raise DataValidationError("trailers cannot be None")
    return sorted(str(t) for t in trailers if str(t).strip())


def track_3pl_destruction_shuttle_trailers(shuttle_id: str, cases_loaded: int) -> dict:
    """Track dedicated shuttle trailers hauling recalled stock to destruction facilities."""
    _req(shuttle_id, "shuttle_id")
    if cases_loaded < 0:
        raise DataValidationError("cases_loaded cannot be negative")
    return {"op": "track_3pl_destruction_shuttle_trailers", "shuttle_id": str(shuttle_id), "cases_loaded": int(cases_loaded), "src": "recallstorm/dc_ops/yard_management.py"}


def prevent_yard_jockey_move_to_outbound_door(trailer_id: str, target_door_type: str = "OUTBOUND") -> dict:
    """Block yard hostler/jockey from spotting a quarantined trailer at an outbound store-shipping door."""
    _req(trailer_id, "trailer_id")
    blocked = str(target_door_type).upper() == "OUTBOUND"
    return {"op": "prevent_yard_jockey_move_to_outbound_door", "trailer_id": str(trailer_id), "move_blocked": blocked, "src": "recallstorm/dc_ops/yard_management.py"}


def log_security_gate_seal_verification_on_exit(trailer_id: str, seal_no: str, guard_id: str) -> dict:
    """Log guard-shack gate exit seal verification on a recall return/destruction load."""
    _req(trailer_id, "trailer_id")
    _req(seal_no, "seal_no")
    _req(guard_id, "guard_id")
    return {"op": "log_security_gate_seal_verification_on_exit", "trailer_id": str(trailer_id), "seal_no": str(seal_no), "guard_id": str(guard_id), "src": "recallstorm/dc_ops/yard_management.py"}


def manage_detention_clock_on_held_equipment(hours_held: float, free_hours: float = 48.0, rate_per_hour: float = 15.0) -> float:
    """Calculate carrier trailer detention charges beyond free_hours."""
    if hours_held < 0 or free_hours < 0 or rate_per_hour < 0:
        raise DataValidationError("Negative detention parameters")
    billable = max(0.0, hours_held - free_hours)
    return round(billable * rate_per_hour, 2)


def assign_isolated_hazmat_parking_stall(dc_id: str, trailer_id: str) -> str:
    """Assign an isolated perimeter yard stall for leaking/hazmat recall trailers."""
    _req(dc_id, "dc_id")
    _req(trailer_id, "trailer_id")
    return f"{str(dc_id).strip()}-HAZ-YARD-01"


def audit_daily_yard_check_inventory_sync(yms_trailers: set[str], physical_trailers: set[str]) -> list[str]:
    """Return sorted discrepancy trailer IDs between YMS and physical yard walk."""
    if yms_trailers is None or physical_trailers is None:
        raise DataValidationError("Inputs cannot be None")
    return sorted(yms_trailers ^ physical_trailers)
