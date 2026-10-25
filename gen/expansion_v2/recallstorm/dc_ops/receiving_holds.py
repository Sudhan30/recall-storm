"""DC inbound receiving RF blocks, red quarantine LPNs, and OS&D refusals."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class InboundReceivingBlock:
    """WMS inbound receiving RF block for recalled purchase order lines."""

    ref_id: str = "DC-RCV-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class DockDoorQuarantine:
    """Receiving dock door quarantine staging zone."""

    ref_id: str = "DC-DCK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def flag_recalled_po_line_on_receiving_rf(po_id: str, sku_id: str) -> dict:
    """Flag a purchase order line on DC receiving RF guns."""
    _req(po_id, "po_id")
    _req(sku_id, "sku_id")
    return {"op": "flag_recalled_po_line_on_receiving_rf", "po_id": str(po_id), "sku_id": str(sku_id), "flagged": True, "src": "recallstorm/dc_ops/receiving_holds.py"}


def reject_affected_lot_at_inbound_scan(lot_code: str, banned_lots: set[str]) -> dict:
    """Reject an inbound pallet scan if lot_code is in banned_lots."""
    _req(lot_code, "lot_code")
    if banned_lots is None:
        raise DataValidationError("banned_lots cannot be None")
    rejected = str(lot_code).strip().upper() in {str(b).strip().upper() for b in banned_lots}
    return {"op": "reject_affected_lot_at_inbound_scan", "lot_code": str(lot_code), "rejected": rejected, "src": "recallstorm/dc_ops/receiving_holds.py"}


def print_immediate_red_quarantine_pallet_lpn(dc_id: str, seq: int = 1) -> str:
    """Print a red quarantine LPN label at the receiving dock."""
    _req(dc_id, "dc_id")
    if seq <= 0:
        raise DataValidationError("seq must be positive")
    return f"DC-RED-{str(dc_id).strip()}-{seq:04d}"


def segregate_mixed_lot_vendor_ti_hi_pallets(total_cases: int, recalled_cases: int) -> dict:
    """Break down a mixed-lot vendor pallet into clean cases and recalled cases."""
    if total_cases < 0 or recalled_cases < 0 or recalled_cases > total_cases:
        raise DataValidationError("Invalid case counts")
    return {"op": "segregate_mixed_lot_vendor_ti_hi_pallets", "clean_cases": total_cases - recalled_cases, "recalled_cases": recalled_cases, "src": "recallstorm/dc_ops/receiving_holds.py"}


def block_auto_putaway_to_reserve_racking(lpn: str) -> dict:
    """Block WMS from generating a reserve-rack putaway task for a quarantined LPN."""
    _req(lpn, "lpn")
    return {"op": "block_auto_putaway_to_reserve_racking", "lpn": str(lpn), "putaway_blocked": True, "src": "recallstorm/dc_ops/receiving_holds.py"}


def log_driver_detention_for_lot_sorting(trailer_id: str, minutes: float) -> dict:
    """Log lumper/driver detention time spent sorting mixed-lot inbound trailers."""
    _req(trailer_id, "trailer_id")
    if minutes < 0:
        raise DataValidationError("minutes cannot be negative")
    return {"op": "log_driver_detention_for_lot_sorting", "trailer_id": str(trailer_id), "minutes": round(float(minutes), 2), "src": "recallstorm/dc_ops/receiving_holds.py"}


def capture_inbound_bol_and_lumper_notes(bol_id: str, notes: str) -> dict:
    """Capture receiving BOL and lumper sortation notes."""
    _req(bol_id, "bol_id")
    _req(notes, "notes")
    return {"op": "capture_inbound_bol_and_lumper_notes", "bol_id": str(bol_id), "notes": str(notes), "src": "recallstorm/dc_ops/receiving_holds.py"}


def alert_dc_qa_inspector_to_receiving_dock(dc_id: str, door_no: int) -> dict:
    """Page DC Quality Assurance inspector to door_no."""
    _req(dc_id, "dc_id")
    if door_no <= 0:
        raise DataValidationError("door_no must be positive")
    return {"op": "alert_dc_qa_inspector_to_receiving_dock", "dc_id": str(dc_id), "door_no": int(door_no), "src": "recallstorm/dc_ops/receiving_holds.py"}


def generate_osd_over_short_damage_refusal(po_id: str, refused_cases: int) -> dict:
    """Generate an OS&D (Over, Short & Damaged / Recall Refusal) claim at receiving."""
    _req(po_id, "po_id")
    if refused_cases <= 0:
        raise DataValidationError("refused_cases must be positive")
    return {"op": "generate_osd_over_short_damage_refusal", "po_id": str(po_id), "refused_cases": int(refused_cases), "src": "recallstorm/dc_ops/receiving_holds.py"}


def release_clean_lots_on_split_delivery(po_id: str, clean_cases: int) -> dict:
    """Release verified clean lots from a split delivery to active reserve stock."""
    _req(po_id, "po_id")
    if clean_cases < 0:
        raise DataValidationError("clean_cases cannot be negative")
    return {"op": "release_clean_lots_on_split_delivery", "po_id": str(po_id), "clean_cases": int(clean_cases), "src": "recallstorm/dc_ops/receiving_holds.py"}
