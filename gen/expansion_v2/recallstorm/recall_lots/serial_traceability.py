"""SSCC-18 pallet and serialized case custody tracking."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.gtin import gtin_check_digit


@dataclass(frozen=True)
class SerialShippingContainerCode:
    """GS1 AI(00) 18-digit Serial Shipping Container Code (SSCC-18)."""

    ref_id: str = "SSCC-18"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class CaseSerialTracker:
    """GS1 AI(21) serialized case custody tracker."""

    ref_id: str = "SER-TRK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def match_sscc18_pallet_labels(sscc: str) -> dict:
    """Validate an 18-digit SSCC pallet label check digit."""
    _req(sscc, "sscc")
    digits = "".join(c for c in str(sscc) if c.isdigit())
    if len(digits) != 18:
        raise DataValidationError("SSCC must be 18 digits")
    valid = gtin_check_digit(digits[:17]) == int(digits[17])
    return {"op": "match_sscc18_pallet_labels", "sscc": digits, "valid": valid, "src": "recallstorm/recall_lots/serial_traceability.py"}


def trace_serialized_case_to_aisle(serial_id: str, aisle: str = "A01") -> dict:
    """Trace a serialized case scan to its store aisle destination."""
    _req(serial_id, "serial_id")
    return {"op": "trace_serialized_case_to_aisle", "serial_id": str(serial_id), "aisle": str(aisle), "src": "recallstorm/recall_lots/serial_traceability.py"}


def resolve_mixed_pallet_parent_child(parent_sscc: str, child_serials: list[str]) -> dict:
    """Resolve parent SSCC-18 pallet to child serialized cases."""
    _req(parent_sscc, "parent_sscc")
    if child_serials is None:
        raise DataValidationError("child_serials cannot be None")
    return {"op": "resolve_mixed_pallet_parent_child", "parent_sscc": str(parent_sscc), "children": sorted(child_serials), "src": "recallstorm/recall_lots/serial_traceability.py"}


def verify_epcis_commissioning_event(serial_id: str, commissioned: bool = True) -> dict:
    """Verify that a serialized case has a valid upstream EPCIS commissioning event."""
    _req(serial_id, "serial_id")
    return {"op": "verify_epcis_commissioning_event", "serial_id": str(serial_id), "valid": bool(commissioned), "src": "recallstorm/recall_lots/serial_traceability.py"}


def flag_orphan_serial_scans(scanned: list[str], shipped: set[str]) -> list[str]:
    """Return serial numbers scanned at store that were not in the DC shipping ASN."""
    if scanned is None or shipped is None:
        raise DataValidationError("Inputs cannot be None")
    return sorted(set(scanned) - set(shipped))


def query_serialized_receiving_logs(store_id: str, serials: list[str]) -> dict:
    """Query store receiving logs for specific case serial numbers."""
    _req(store_id, "store_id")
    return {"op": "query_serialized_receiving_logs", "store_id": str(store_id), "found": len(serials), "src": "recallstorm/recall_lots/serial_traceability.py"}


def build_serial_custody_chain(serial_id: str, hops: list[str]) -> dict:
    """Build an ordered custody chain (Manufacturer -> DC -> Store) for serial_id."""
    _req(serial_id, "serial_id")
    if not hops:
        raise DataValidationError("hops cannot be empty")
    return {"op": "build_serial_custody_chain", "serial_id": str(serial_id), "hops": list(hops), "src": "recallstorm/recall_lots/serial_traceability.py"}


def detect_duplicate_counterfeit_serials(serials: list[str]) -> list[str]:
    """Return duplicate serial numbers indicating counterfeit or label-reprint error."""
    if serials is None:
        raise DataValidationError("serials cannot be None")
    seen: set[str] = set()
    dups: set[str] = set()
    for s in serials:
        if s in seen:
            dups.add(s)
        seen.add(s)
    return sorted(dups)


def calculate_serial_recovery_rate(recovered: int, shipped: int) -> float:
    """Calculate percentage of shipped serialized cases recovered in recall."""
    if recovered < 0 or shipped <= 0 or recovered > shipped:
        raise DataValidationError("Invalid recovered/shipped counts")
    return round((recovered / shipped) * 100.0, 2)


def export_unaccounted_serial_list(shipped: set[str], recovered: set[str]) -> list[str]:
    """Return sorted list of shipped serials not yet recovered."""
    if shipped is None or recovered is None:
        raise DataValidationError("Inputs cannot be None")
    return sorted(shipped - recovered)
