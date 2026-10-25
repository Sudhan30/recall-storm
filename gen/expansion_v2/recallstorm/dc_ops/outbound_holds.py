"""Outbound wave interception, stretch-wrap pulls, and shipping lane purges."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class OutboundWaveInterceptor:
    """Interceptor for active DC outbound store order pick waves."""

    ref_id: str = "DC-WAV-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class ShippingDockPurge:
    """Shipping lane and trailer purge before outbound truck departure."""

    ref_id: str = "DC-SHP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def scan_active_pick_waves_for_recalled_lpn(waves: list[dict], sku_id: str) -> list[str]:
    """Return wave_ids containing sku_id."""
    if waves is None:
        raise DataValidationError("waves cannot be None")
    _req(sku_id, "sku_id")
    return [str(w["wave_id"]) for w in waves if sku_id in w.get("skus", [])]


def intercept_pallet_at_stretch_wrap_station(lpn: str, station_id: str = "WRAP-01") -> dict:
    """Halt automated stretch-wrapper and divert pallet lpn for case stripping."""
    _req(lpn, "lpn")
    return {"op": "intercept_pallet_at_stretch_wrap_station", "lpn": str(lpn), "station_id": str(station_id), "halted": True, "src": "recallstorm/dc_ops/outbound_holds.py"}


def pull_affected_cases_from_store_build_pallet(lpn: str, total_cases: int, pulled_cases: int) -> dict:
    """Strip recalled cases from a multi-SKU store-build pallet."""
    _req(lpn, "lpn")
    if total_cases < 0 or pulled_cases < 0 or pulled_cases > total_cases:
        raise DataValidationError("Invalid case counts")
    return {"op": "pull_affected_cases_from_store_build_pallet", "lpn": str(lpn), "remaining_cases": total_cases - pulled_cases, "src": "recallstorm/dc_ops/outbound_holds.py"}


def halt_loading_of_contaminated_trailer_door(dc_id: str, door_no: int) -> dict:
    """Engage red dock-lock light on outbound shipping door_no."""
    _req(dc_id, "dc_id")
    if door_no <= 0:
        raise DataValidationError("door_no must be positive")
    return {"op": "halt_loading_of_contaminated_trailer_door", "dc_id": str(dc_id), "door_no": int(door_no), "dock_locked": True, "src": "recallstorm/dc_ops/outbound_holds.py"}


def reprint_adjusted_store_shipping_manifest(manifest_id: str, cut_cases: int) -> dict:
    """Reprint store shipping manifest and EDI 856 ASN after removing recalled cases."""
    _req(manifest_id, "manifest_id")
    if cut_cases < 0:
        raise DataValidationError("cut_cases cannot be negative")
    return {"op": "reprint_adjusted_store_shipping_manifest", "manifest_id": str(manifest_id), "cut_cases": int(cut_cases), "src": "recallstorm/dc_ops/outbound_holds.py"}


def scan_staged_shipping_lanes_with_rfid(lane_id: str, epc_tags_found: int = 0) -> dict:
    """Sweep staged outbound shipping lanes with overhead/handheld RFID readers."""
    _req(lane_id, "lane_id")
    if epc_tags_found < 0:
        raise DataValidationError("epc_tags_found cannot be negative")
    return {"op": "scan_staged_shipping_lanes_with_rfid", "lane_id": str(lane_id), "clear": epc_tags_found == 0, "src": "recallstorm/dc_ops/outbound_holds.py"}


def prevent_bol_print_until_hold_cleared(trailer_id: str, holds_open: int = 0) -> dict:
    """Block shipping office from printing the outbound Bill of Lading while any recall hold is open on trailer_id."""
    _req(trailer_id, "trailer_id")
    if holds_open < 0:
        raise DataValidationError("holds_open cannot be negative")
    return {"op": "prevent_bol_print_until_hold_cleared", "trailer_id": str(trailer_id), "bol_allowed": holds_open == 0, "src": "recallstorm/dc_ops/outbound_holds.py"}


def log_late_truck_departure_delay_reason(truck_id: str, delay_mins: int) -> dict:
    """Log excused recall-purge delay on outbound store delivery truck."""
    _req(truck_id, "truck_id")
    if delay_mins < 0:
        raise DataValidationError("delay_mins cannot be negative")
    return {"op": "log_late_truck_departure_delay_reason", "truck_id": str(truck_id), "delay_mins": int(delay_mins), "reason": "RECALL_DOCK_PURGE", "src": "recallstorm/dc_ops/outbound_holds.py"}


def re_cube_shorted_store_delivery_trailer(orig_cube_ft3: float, removed_cube_ft3: float) -> float:
    """Recalculate trailer cube utilization after stripping recalled pallets."""
    if orig_cube_ft3 < 0 or removed_cube_ft3 < 0 or removed_cube_ft3 > orig_cube_ft3:
        raise DataValidationError("Invalid cube values")
    return round(orig_cube_ft3 - removed_cube_ft3, 2)


def confirm_clean_outbound_seal_application(trailer_id: str, new_seal_no: str) -> dict:
    """Record new security seal number applied after breaking seal to strip recalled cases."""
    _req(trailer_id, "trailer_id")
    _req(new_seal_no, "new_seal_no")
    return {"op": "confirm_clean_outbound_seal_application", "trailer_id": str(trailer_id), "seal_no": str(new_seal_no), "src": "recallstorm/dc_ops/outbound_holds.py"}
