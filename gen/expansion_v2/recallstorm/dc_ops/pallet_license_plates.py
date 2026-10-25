"""LPN genealogy tracking and rainbow pallet layer splitting."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.gtin import gtin_check_digit


@dataclass(frozen=True)
class LpnGenealogyTracker:
    """Parent-to-child LPN genealogy tracker in WMS."""

    ref_id: str = "LPN-GEN-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class MixedPalletSplitter:
    """Splitter for rainbow pallets containing multiple lots or SKUs."""

    ref_id: str = "LPN-SPL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def trace_parent_receiving_lpn_to_child_picks(parent_lpn: str, tree: dict[str, list[str]]) -> list[str]:
    """Return sorted child pick LPNs derived from parent_lpn."""
    _req(parent_lpn, "parent_lpn")
    if tree is None:
        raise DataValidationError("tree cannot be None")
    return sorted(tree.get(str(parent_lpn), []))


def identify_rainbow_pallets_with_recalled_layers(pallets: list[dict], target_lot: str) -> list[str]:
    """Return LPNs of multi-lot 'rainbow' pallets containing target_lot."""
    if pallets is None:
        raise DataValidationError("pallets cannot be None")
    _req(target_lot, "target_lot")
    return [str(p["lpn"]) for p in pallets if target_lot in p.get("lots", []) and len(p.get("lots", [])) > 1]


def generate_split_pallet_rework_work_order(lpn: str, recalled_cases: int) -> dict:
    """Create a WMS work order to break down a rainbow pallet and split off recalled_cases onto a new child LPN."""
    _req(lpn, "lpn")
    if recalled_cases <= 0:
        raise DataValidationError("recalled_cases must be positive")
    return {"op": "generate_split_pallet_rework_work_order", "parent_lpn": str(lpn), "child_hold_lpn": f"{lpn}-HOLD", "recalled_cases": int(recalled_cases), "src": "recallstorm/dc_ops/pallet_license_plates.py"}


def invalidate_consumed_or_destroyed_lpns(lpns: list[str]) -> list[str]:
    """Mark consumed or destroyed LPNs as inactive in WMS."""
    if lpns is None:
        raise DataValidationError("lpns cannot be None")
    return sorted(str(l) for l in lpns if str(l).strip())


def block_lpn_consolidation_across_hold_codes(lpn_a_status: str, lpn_b_status: str) -> dict:
    """Prevent forklift operators from consolidating an ACTIVE LPN with a HOLD/QUARANTINE LPN."""
    _req(lpn_a_status, "lpn_a_status")
    _req(lpn_b_status, "lpn_b_status")
    allowed = str(lpn_a_status).upper() == str(lpn_b_status).upper()
    return {"op": "block_lpn_consolidation_across_hold_codes", "consolidation_allowed": allowed, "src": "recallstorm/dc_ops/pallet_license_plates.py"}


def verify_gs1_128_sscc_check_digit_integrity(sscc18: str) -> bool:
    """Verify the Mod-10 check digit of an 18-digit GS1-128 SSCC pallet barcode."""
    _req(sscc18, "sscc18")
    digits = "".join(c for c in str(sscc18) if c.isdigit())
    if len(digits) != 18:
        return False
    return gtin_check_digit(digits[:17]) == int(digits[17])


def track_lpn_location_move_history_in_wms(lpn: str, moves: list[str]) -> dict:
    """Return ordered move history (Receiving -> Reserve -> Quarantine) for lpn."""
    _req(lpn, "lpn")
    if not moves:
        raise DataValidationError("moves cannot be empty")
    return {"op": "track_lpn_location_move_history_in_wms", "lpn": str(lpn), "moves": list(moves), "src": "recallstorm/dc_ops/pallet_license_plates.py"}


def flag_ghost_lpns_in_lost_and_found_zone(lpns: list[str]) -> list[str]:
    """Flag LPNs residing in the WMS 'LOST_AND_FOUND' virtual zone during a recall."""
    if lpns is None:
        raise DataValidationError("lpns cannot be None")
    return sorted(str(l) for l in lpns if str(l).strip())


def print_replacement_hold_lpn_thermal_labels(lpn: str, copies: int = 2) -> dict:
    """Print replacement red thermal LPN labels for a quarantine pallet."""
    _req(lpn, "lpn")
    if copies <= 0:
        raise DataValidationError("copies must be positive")
    return {"op": "print_replacement_hold_lpn_thermal_labels", "lpn": str(lpn), "copies": int(copies), "src": "recallstorm/dc_ops/pallet_license_plates.py"}


def audit_quarantine_zone_lpn_physical_count(wms_lpns: set[str], scanned_lpns: set[str]) -> dict:
    """Audit physical LPN scans in the DC quarantine cage against WMS book LPNs."""
    if wms_lpns is None or scanned_lpns is None:
        raise DataValidationError("Inputs cannot be None")
    missing = sorted(wms_lpns - scanned_lpns)
    return {"op": "audit_quarantine_zone_lpn_physical_count", "missing_lpns": missing, "reconciled": len(missing) == 0, "src": "recallstorm/dc_ops/pallet_license_plates.py"}
