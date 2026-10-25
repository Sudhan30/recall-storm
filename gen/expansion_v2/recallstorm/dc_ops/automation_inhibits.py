"""AS/RS crane, Symbotic bot, and high-speed unit sorter inhibits."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class AsrsCraneLockout:
    """Automated Storage & Retrieval System (AS/RS) crane lockout."""

    ref_id: str = "AUT-CRN-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class SymboticBotQuarantine:
    """Autonomous case-handling robot (Symbotic / Witron) quarantine inhibit."""

    ref_id: str = "AUT-BOT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def lock_autostore_or_symbotic_storage_bins(cell_id: str, bin_ids: list[str]) -> dict:
    """Lock automated storage bins or bot shelves containing recalled inventory."""
    _req(cell_id, "cell_id")
    if not bin_ids:
        raise DataValidationError("bin_ids cannot be empty")
    return {"op": "lock_autostore_or_symbotic_storage_bins", "cell_id": str(cell_id), "bins": sorted(bin_ids), "locked": True, "src": "recallstorm/dc_ops/automation_inhibits.py"}


def inhibit_depalletizer_robot_layer_pick(robot_id: str, sku_id: str) -> dict:
    """Halt robotic layer depalletizer from induction of sku_id onto conveyor network."""
    _req(robot_id, "robot_id")
    _req(sku_id, "sku_id")
    return {"op": "inhibit_depalletizer_robot_layer_pick", "robot_id": str(robot_id), "sku_id": str(sku_id), "inhibited": True, "src": "recallstorm/dc_ops/automation_inhibits.py"}


def divert_recalled_tote_on_high_speed_sorter(tote_id: str, jackpot_lane: str = "JACKPOT-QA-01") -> dict:
    """Configure Warehouse Control System (WCS) shoe-sorter to kick recalled totes to the QA jackpot lane."""
    _req(tote_id, "tote_id")
    return {"op": "divert_recalled_tote_on_high_speed_sorter", "tote_id": str(tote_id), "diverted_to": str(jackpot_lane), "src": "recallstorm/dc_ops/automation_inhibits.py"}


def purge_unit_sorter_chute_accumulations(chute_id: str, units: int) -> dict:
    """Purge accumulated eaches of a recalled SKU from tilt-tray/cross-belt sorter chutes."""
    _req(chute_id, "chute_id")
    if units < 0:
        raise DataValidationError("units cannot be negative")
    return {"op": "purge_unit_sorter_chute_accumulations", "chute_id": str(chute_id), "units": int(units), "src": "recallstorm/dc_ops/automation_inhibits.py"}


def prevent_agv_forklift_autonomous_putaway(agv_id: str, lpn: str) -> dict:
    """Cancel autonomous guided vehicle (AGV) putaway mission for a recalled LPN."""
    _req(agv_id, "agv_id")
    _req(lpn, "lpn")
    return {"op": "prevent_agv_forklift_autonomous_putaway", "agv_id": str(agv_id), "lpn": str(lpn), "cancelled": True, "src": "recallstorm/dc_ops/automation_inhibits.py"}


def isolate_faulted_broken_case_in_shuttle_aisle(aisle_id: str, level: int) -> dict:
    """Lock out a shuttle-rack aisle level when a recalled liquid/glass case leaks on the deck."""
    _req(aisle_id, "aisle_id")
    if level <= 0:
        raise DataValidationError("level must be positive")
    return {"op": "isolate_faulted_broken_case_in_shuttle_aisle", "aisle_id": str(aisle_id), "level": int(level), "isolated": True, "src": "recallstorm/dc_ops/automation_inhibits.py"}


def sync_wcs_warehouse_control_with_wms_hold(wms_holds: set[str], wcs_holds: set[str]) -> dict:
    """Verify sub-second synchronization between WMS inventory holds and WCS conveyor PLC tables."""
    if wms_holds is None or wcs_holds is None:
        raise DataValidationError("Hold sets cannot be None")
    missing = sorted(wms_holds - wcs_holds)
    return {"op": "sync_wcs_warehouse_control_with_wms_hold", "in_sync": len(missing) == 0, "missing_in_wcs": missing, "src": "recallstorm/dc_ops/automation_inhibits.py"}


def schedule_maintenance_retrieval_of_locked_tote(tote_id: str, decant_station: str = "DECANT-QA") -> dict:
    """Command automation cell to route a quarantined storage tote to a dedicated QA decant workstation."""
    _req(tote_id, "tote_id")
    return {"op": "schedule_maintenance_retrieval_of_locked_tote", "tote_id": str(tote_id), "station": str(decant_station), "src": "recallstorm/dc_ops/automation_inhibits.py"}


def audit_automated_storage_quarantine_inventory(cell_id: str, held_cases: int) -> dict:
    """Audit total recalled cases held inside automated mechatronics cells."""
    _req(cell_id, "cell_id")
    if held_cases < 0:
        raise DataValidationError("held_cases cannot be negative")
    return {"op": "audit_automated_storage_quarantine_inventory", "cell_id": str(cell_id), "held_cases": int(held_cases), "src": "recallstorm/dc_ops/automation_inhibits.py"}


def restore_mechatronics_cell_to_production(cell_id: str, cleared_by_qa: bool = True) -> dict:
    """Restore an automated storage cell to production after recall purge."""
    _req(cell_id, "cell_id")
    return {"op": "restore_mechatronics_cell_to_production", "cell_id": str(cell_id), "online": bool(cleared_by_qa), "src": "recallstorm/dc_ops/automation_inhibits.py"}
