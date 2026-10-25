"""DC -10F freezer quarantine zones and multi-temp bulkhead audits."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class FreezerBlastHold:
    """DC -10F sub-zero freezer quarantine hold."""

    ref_id: str = "CLD-FRZ-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ColdRoomSegregation:
    """Segregation rules for DC refrigerated/frozen rooms."""

    ref_id: str = "CLD-SEG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def verify_minus_ten_f_freezer_quarantine_zone(temp_f: float, max_temp_f: float = 0.0) -> dict:
    """Verify that DC freezer quarantine cage maintains <= 0.0F (target -10F) to preserve evidence samples."""
    return {"op": "verify_minus_ten_f_freezer_quarantine_zone", "compliant": float(temp_f) <= float(max_temp_f), "temp_f": float(temp_f), "src": "recallstorm/dc_ops/cold_storage_holds.py"}


def monitor_ammonia_leak_exposure_in_cold_room(ammonia_ppm: float, limit_ppm: float = 25.0) -> dict:
    """Check anhydrous ammonia refrigeration leak sensors (quarantine all exposed food if > limit_ppm)."""
    if ammonia_ppm < 0 or limit_ppm <= 0:
        raise DataValidationError("Invalid ammonia_ppm")
    return {"op": "monitor_ammonia_leak_exposure_in_cold_room", "quarantine_room": ammonia_ppm >= limit_ppm, "ppm": float(ammonia_ppm), "src": "recallstorm/dc_ops/cold_storage_holds.py"}


def track_ice_cream_shrink_from_dock_staging(dock_minutes: float, max_minutes: float = 20.0) -> dict:
    """Flag frozen dairy pallets staged on a 38F cold dock longer than 20 minutes."""
    if dock_minutes < 0 or max_minutes <= 0:
        raise DataValidationError("Invalid dock_minutes")
    return {"op": "track_ice_cream_shrink_from_dock_staging", "melted_risk": dock_minutes > max_minutes, "src": "recallstorm/dc_ops/cold_storage_holds.py"}


def allocate_insulated_pallet_covers_for_returns(pallets: int) -> int:
    """Allocate insulated thermal pallet blankets for store frozen recall returns."""
    if pallets < 0:
        raise DataValidationError("pallets cannot be negative")
    return int(pallets)


def prevent_blast_cell_cross_airflow_risk(cell_id: str,leaking_package: bool = False) -> dict:
    """Prevent placing unsealed/damaged pathogen-recalled cases directly in front of high-velocity blast freezer fans."""
    _req(cell_id, "cell_id")
    return {"op": "prevent_blast_cell_cross_airflow_risk", "cell_id": str(cell_id), "overwrap_required": bool(leaking_package), "src": "recallstorm/dc_ops/cold_storage_holds.py"}


def schedule_defrost_window_for_held_coils(room_id: str, hour_of_day: int = 3) -> dict:
    """Schedule evaporator coil defrost cycle during off-peak hours."""
    _req(room_id, "room_id")
    if not (0 <= hour_of_day <= 23):
        raise DataValidationError("hour_of_day must be in 0..23")
    return {"op": "schedule_defrost_window_for_held_coils", "room_id": str(room_id), "hour": int(hour_of_day), "src": "recallstorm/dc_ops/cold_storage_holds.py"}


def log_cold_suit_labor_rotation_limits(minutes_in_freezer: float, max_continuous_mins: float = 45.0) -> dict:
    """Enforce warm-up break rotation for DC associates pulling recall pallets in -10F freezers."""
    if minutes_in_freezer < 0 or max_continuous_mins <= 0:
        raise DataValidationError("Invalid minutes")
    return {"op": "log_cold_suit_labor_rotation_limits", "warmup_break_due": minutes_in_freezer >= max_continuous_mins, "src": "recallstorm/dc_ops/cold_storage_holds.py"}


def validate_frozen_destruction_rendering_chain(renderer_id: str, anaerobic_digester: bool = True) -> dict:
    """Validate disposal of frozen meat/dairy recalls via licensed rendering or anaerobic digestion."""
    _req(renderer_id, "renderer_id")
    return {"op": "validate_frozen_destruction_rendering_chain", "renderer_id": str(renderer_id), "approved": bool(anaerobic_digester), "src": "recallstorm/dc_ops/cold_storage_holds.py"}


def audit_multi_temp_trailer_bulkhead_position(trailer_id: str, bulkhead_sealed: bool = True) -> dict:
    """Audit movable insulated bulkhead seal in multi-zone (-10F / 34F / 55F) trailers."""
    _req(trailer_id, "trailer_id")
    return {"op": "audit_multi_temp_trailer_bulkhead_position", "trailer_id": str(trailer_id), "compliant": bool(bulkhead_sealed), "src": "recallstorm/dc_ops/cold_storage_holds.py"}


def release_tempered_product_with_qa_signoff(lpn: str, qa_id: str) -> dict:
    """Authorize controlled slack-out/tempering release of safe product with QA sign-off."""
    _req(lpn, "lpn")
    _req(qa_id, "qa_id")
    return {"op": "release_tempered_product_with_qa_signoff", "lpn": str(lpn), "qa_id": str(qa_id), "src": "recallstorm/dc_ops/cold_storage_holds.py"}
