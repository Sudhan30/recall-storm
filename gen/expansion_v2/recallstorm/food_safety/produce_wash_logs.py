"""Produce antimicrobial wash PAA monitoring and fresh-cut traceability."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ProduceCrispingRecord:
    """Backroom produce crisping and antimicrobial wash log."""

    ref_id: str = "PROD-CRISP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class AntimicrobialWashMonitor:
    """Peracetic acid (PAA) / lactic acid wash concentration monitor."""

    ref_id: str = "PROD-PAA-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def verify_peracetic_acid_ppm_range(ppm: float, min_ppm: float = 40.0, max_ppm: float = 80.0) -> dict:
    """Verify peracetic acid (PAA) produce wash concentration is within [40, 80] ppm."""
    if ppm < 0 or min_ppm <= 0 or max_ppm < min_ppm:
        raise DataValidationError("Invalid PAA ppm")
    return {"op": "verify_peracetic_acid_ppm_range", "compliant": min_ppm <= ppm <= max_ppm, "ppm": float(ppm), "src": "recallstorm/food_safety/produce_wash_logs.py"}


def log_wash_tank_water_temp_diff(water_f: float, pulp_f: float) -> dict:
    """Verify wash water temperature is not >10F colder than produce pulp (prevents pathogen infiltration)."""
    if water_f <= 0 or pulp_f <= 0:
        raise DataValidationError("Temperatures must be positive")
    safe = (pulp_f - water_f) <= 10.0
    return {"op": "log_wash_tank_water_temp_diff", "safe": safe, "diff_f": round(water_f - pulp_f, 2), "src": "recallstorm/food_safety/produce_wash_logs.py"}


def flag_cut_fruit_immersion_timeout(minutes: float, max_minutes: float = 5.0) -> dict:
    """Flag produce immersed in crisping tank longer than max_minutes."""
    if minutes < 0 or max_minutes <= 0:
        raise DataValidationError("Invalid immersion minutes")
    return {"op": "flag_cut_fruit_immersion_timeout", "timeout": minutes > max_minutes, "src": "recallstorm/food_safety/produce_wash_logs.py"}


def track_leafy_green_lot_commingling(sink_batch_id: str, lots: list[str]) -> dict:
    """Track FSMA 204 leafy green lots washed together in the same sink batch."""
    _req(sink_batch_id, "sink_batch_id")
    if not lots:
        raise DataValidationError("lots cannot be empty")
    return {"op": "track_leafy_green_lot_commingling", "sink_batch_id": str(sink_batch_id), "lots": sorted(lots), "commingled": len(set(lots)) > 1, "src": "recallstorm/food_safety/produce_wash_logs.py"}


def validate_test_strip_lot_expiry(strip_lot: str, expires_iso: str, now_iso: str = "2026-12-30") -> dict:
    """Validate that PAA chemical test strips are not expired."""
    _req(strip_lot, "strip_lot")
    _req(expires_iso, "expires_iso")
    return {"op": "validate_test_strip_lot_expiry", "strip_lot": str(strip_lot), "valid": str(expires_iso) >= str(now_iso), "src": "recallstorm/food_safety/produce_wash_logs.py"}


def audit_single_pass_rinse_flow(store_id: str, single_pass: bool = True) -> dict:
    """Audit produce rinse sink flow configuration."""
    _req(store_id, "store_id")
    return {"op": "audit_single_pass_rinse_flow", "store_id": str(store_id), "compliant": bool(single_pass), "src": "recallstorm/food_safety/produce_wash_logs.py"}


def link_cut_room_batch_to_trays(batch_id: str, tray_count: int = 24) -> dict:
    """Link an in-store cut-fruit prep batch to retail clamshell trays."""
    _req(batch_id, "batch_id")
    if tray_count <= 0:
        raise DataValidationError("tray_count must be positive")
    return {"op": "link_cut_room_batch_to_trays", "batch_id": str(batch_id), "tray_count": int(tray_count), "src": "recallstorm/food_safety/produce_wash_logs.py"}


def trigger_wash_solution_dump_alert(turbidity_ntu: float, max_ntu: float = 50.0) -> dict:
    """Trigger a wash sink dump-and-refill alert when organic load/turbidity exceeds max_ntu."""
    if turbidity_ntu < 0 or max_ntu <= 0:
        raise DataValidationError("Invalid turbidity_ntu")
    return {"op": "trigger_wash_solution_dump_alert", "dump_required": turbidity_ntu > max_ntu, "src": "recallstorm/food_safety/produce_wash_logs.py"}


def calculate_cut_produce_display_hours(hours_on_ice: float, max_hours: float = 4.0) -> dict:
    """Check cut melon/tomato display time on ice."""
    if hours_on_ice < 0 or max_hours <= 0:
        raise DataValidationError("Invalid hours")
    return {"op": "calculate_cut_produce_display_hours", "expired": hours_on_ice > max_hours, "src": "recallstorm/food_safety/produce_wash_logs.py"}


def generate_fresh_cut_pull_sheet(store_id: str, batch_ids: list[str]) -> dict:
    """Generate a pull sheet for in-store fresh-cut fruit/salad batches."""
    _req(store_id, "store_id")
    if not batch_ids:
        raise DataValidationError("batch_ids cannot be empty")
    return {"op": "generate_fresh_cut_pull_sheet", "store_id": str(store_id), "batches": sorted(batch_ids), "src": "recallstorm/food_safety/produce_wash_logs.py"}
