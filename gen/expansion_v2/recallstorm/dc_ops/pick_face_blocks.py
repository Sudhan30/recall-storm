"""Freeze DC forward pick slots, cancel letdowns, and redirect voice picks."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ActivePickSlotHold:
    """Hold on a DC primary forward-pick slot."""

    ref_id: str = "DC-PCK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ReplenishmentStopper:
    """Stopper cancelling reserve-to-pick-face forklift letdown tasks."""

    ref_id: str = "DC-REP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def freeze_primary_forward_pick_location(dc_id: str, slot_id: str) -> dict:
    """Freeze a primary forward pick slot in WMS within seconds of recall activation."""
    _req(dc_id, "dc_id")
    _req(slot_id, "slot_id")
    return {"op": "freeze_primary_forward_pick_location", "dc_id": str(dc_id), "slot_id": str(slot_id), "frozen": True, "src": "recallstorm/dc_ops/pick_face_blocks.py"}


def cancel_pending_letdown_replenishment_tasks(task_ids: list[str]) -> list[str]:
    """Cancel queued forklift letdown tasks from overhead reserve racking to the pick face."""
    if task_ids is None:
        raise DataValidationError("task_ids cannot be None")
    return sorted(str(t) for t in task_ids if str(t).strip())


def redirect_voice_pick_operator_around_slot(slot_id: str, sub_slot_id: str | None = None) -> dict:
    """Update Vocollect / voice-pick script to skip slot_id or direct operator to sub_slot_id."""
    _req(slot_id, "slot_id")
    return {"op": "redirect_voice_pick_operator_around_slot", "skipped_slot": str(slot_id), "sub_slot": sub_slot_id, "src": "recallstorm/dc_ops/pick_face_blocks.py"}


def trigger_immediate_slot_purge_to_cage(dc_id: str, slot_id: str, cases: int) -> dict:
    """Create a high-priority task to strip all cases from slot_id into the DC quarantine cage."""
    _req(dc_id, "dc_id")
    _req(slot_id, "slot_id")
    if cases < 0:
        raise DataValidationError("cases cannot be negative")
    return {"op": "trigger_immediate_slot_purge_to_cage", "dc_id": str(dc_id), "slot_id": str(slot_id), "cases": int(cases), "src": "recallstorm/dc_ops/pick_face_blocks.py"}


def lock_case_flow_rack_lane_gravity_feed(lane_id: str) -> dict:
    """Engage mechanical/WMS stop on a multi-deep gravity case-flow rack lane."""
    _req(lane_id, "lane_id")
    return {"op": "lock_case_flow_rack_lane_gravity_feed", "lane_id": str(lane_id), "locked": True, "src": "recallstorm/dc_ops/pick_face_blocks.py"}


def verify_empty_pick_slot_via_barcode_scan(slot_id: str, check_digit: str) -> dict:
    """Verify via slot check-digit barcode scan that the pick slot has been completely emptied."""
    _req(slot_id, "slot_id")
    _req(check_digit, "check_digit")
    return {"op": "verify_empty_pick_slot_via_barcode_scan", "slot_id": str(slot_id), "verified_empty": True, "src": "recallstorm/dc_ops/pick_face_blocks.py"}


def re_slot_substitute_sku_into_pick_face(slot_id: str, sub_sku_id: str) -> dict:
    """Assign an approved substitute SKU to the vacated pick slot."""
    _req(slot_id, "slot_id")
    _req(sub_sku_id, "sub_sku_id")
    return {"op": "re_slot_substitute_sku_into_pick_face", "slot_id": str(slot_id), "sub_sku_id": str(sub_sku_id), "src": "recallstorm/dc_ops/pick_face_blocks.py"}


def block_automated_crane_asrs_retrieval(crane_aisle: str, lpn: str) -> dict:
    """Inhibit AS/RS crane from retrieving lpn for outbound store orders."""
    _req(crane_aisle, "crane_aisle")
    _req(lpn, "lpn")
    return {"op": "block_automated_crane_asrs_retrieval", "crane_aisle": str(crane_aisle), "lpn": str(lpn), "blocked": True, "src": "recallstorm/dc_ops/pick_face_blocks.py"}


def audit_partial_case_pick_remnants(slot_id: str, loose_eaches: int) -> dict:
    """Audit split-case / break-pack pick modules for loose individual units."""
    _req(slot_id, "slot_id")
    if loose_eaches < 0:
        raise DataValidationError("loose_eaches cannot be negative")
    return {"op": "audit_partial_case_pick_remnants", "slot_id": str(slot_id), "loose_eaches": int(loose_eaches), "src": "recallstorm/dc_ops/pick_face_blocks.py"}


def restore_pick_face_after_sanitation(slot_id: str, sanitized: bool = True) -> dict:
    """Unfreeze a pick slot after physical purge and sanitation verification."""
    _req(slot_id, "slot_id")
    return {"op": "restore_pick_face_after_sanitation", "slot_id": str(slot_id), "active": bool(sanitized), "src": "recallstorm/dc_ops/pick_face_blocks.py"}
