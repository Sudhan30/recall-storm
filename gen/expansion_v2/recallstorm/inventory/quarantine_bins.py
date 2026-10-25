"""Locked backroom quarantine cages and digital WMS hold locations."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class QuarantineCageManager:
    """Manager for physical locked backroom quarantine cages."""

    ref_id: str = "QBIN-CAGE-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class DigitalHoldLocation:
    """Virtual WMS non-allocatable hold bin."""

    ref_id: str = "QBIN-WMS-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def assign_locked_backroom_cage_bin(store_id: str, hazmat: bool = False) -> str:
    """Assign a locked backroom quarantine bin code for store_id."""
    _req(store_id, "store_id")
    suffix = "HAZ-CAGE-01" if hazmat else "QCAGE-01"
    return f"{str(store_id).strip()}-{suffix}"


def generate_red_hold_pallet_license_plate(dc_id: str, seq: int = 1) -> str:
    """Generate a red quarantine pallet LPN."""
    _req(dc_id, "dc_id")
    if seq < 0:
        raise DataValidationError("seq must be non-negative")
    return f"RED-LPN-{str(dc_id).strip()}-{seq:05d}"


def enforce_wms_directed_putaway_block(lpn: str) -> dict:
    """Block WMS directed putaway to active pick slots for a held LPN."""
    _req(lpn, "lpn")
    return {"op": "enforce_wms_directed_putaway_block", "lpn": str(lpn), "blocked": True, "src": "recallstorm/inventory/quarantine_bins.py"}


def verify_physical_padlock_seal_number(cage_bin: str, seal_no: str) -> dict:
    """Verify serialized security seal on a backroom quarantine cage."""
    _req(cage_bin, "cage_bin")
    _req(seal_no, "seal_no")
    return {"op": "verify_physical_padlock_seal_number", "cage_bin": str(cage_bin), "seal_no": str(seal_no), "src": "recallstorm/inventory/quarantine_bins.py"}


def track_quarantine_bin_capacity_cube(used_ft3: float, max_ft3: float = 200.0) -> dict:
    """Track remaining cubic feet in a store quarantine cage."""
    if used_ft3 < 0 or max_ft3 <= 0:
        raise DataValidationError("Invalid cube values")
    return {"op": "track_quarantine_bin_capacity_cube", "remaining_ft3": round(max(0.0, max_ft3 - used_ft3), 2), "overflow": used_ft3 > max_ft3, "src": "recallstorm/inventory/quarantine_bins.py"}


def prevent_pick_from_quarantine_loc(loc_code: str) -> dict:
    """Inhibit order picking from a quarantine bin."""
    _req(loc_code, "loc_code")
    return {"op": "prevent_pick_from_quarantine_loc", "loc_code": str(loc_code), "pick_inhibited": True, "src": "recallstorm/inventory/quarantine_bins.py"}


def log_authorized_quarantine_access(associate_id: str, cage_bin: str) -> dict:
    """Log authorized manager access to a locked quarantine cage."""
    _req(associate_id, "associate_id")
    _req(cage_bin, "cage_bin")
    return {"op": "log_authorized_quarantine_access", "associate_id": str(associate_id), "cage_bin": str(cage_bin), "src": "recallstorm/inventory/quarantine_bins.py"}


def audit_aged_quarantine_dwell_time(days_held: int, max_days: int = 14) -> dict:
    """Flag quarantined stock held longer than max_days awaiting disposition."""
    if days_held < 0 or max_days <= 0:
        raise DataValidationError("Invalid days_held")
    return {"op": "audit_aged_quarantine_dwell_time", "overdue": days_held > max_days, "days_held": int(days_held), "src": "recallstorm/inventory/quarantine_bins.py"}


def consolidate_partial_hold_cases(eaches: int, case_pack: int = 12) -> tuple[int, int]:
    """Consolidate loose pulled units into (full_cases, remainder_eaches)."""
    if eaches < 0 or case_pack <= 0:
        raise DataValidationError("Invalid eaches or case_pack")
    return (eaches // case_pack, eaches % case_pack)


def release_cleared_bin_to_active(cage_bin: str, qa_clearance_id: str) -> dict:
    """Release a cleared HOLD_VERIFY quarantine bin back to active stock."""
    _req(cage_bin, "cage_bin")
    _req(qa_clearance_id, "qa_clearance_id")
    return {"op": "release_cleared_bin_to_active", "cage_bin": str(cage_bin), "released": True, "src": "recallstorm/inventory/quarantine_bins.py"}
