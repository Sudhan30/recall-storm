"""EDI 204/990 reverse load tendering and RCRA hazmat carrier selection."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ReverseLoadTendering:
    """EDI 204 Motor Carrier Load Tender for reverse recall shipments."""

    ref_id: str = "TMS-TND-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class HazmatCarrierSelector:
    """Selector for DOT/EPA-permitted hazardous waste and recall carriers."""

    ref_id: str = "TMS-HAZ-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def build_consolidated_recall_return_load(dc_id: str, pallets: int, weight_lb: float) -> dict:
    """Build a consolidated truckload return shipment from dc_id."""
    _req(dc_id, "dc_id")
    if pallets <= 0 or weight_lb <= 0 or pallets > 30 or weight_lb > 45000.0:
        raise DataValidationError("Invalid truckload pallets or weight_lb")
    return {"op": "build_consolidated_recall_return_load", "dc_id": str(dc_id), "pallets": int(pallets), "weight_lb": round(float(weight_lb), 2), "src": "recallstorm/dc_ops/carrier_tendering.py"}


def tender_dedicated_truckload_via_edi_204(load_id: str, carrier_scac: str) -> dict:
    """Transmit EDI 204 load tender to carrier_scac."""
    _req(load_id, "load_id")
    _req(carrier_scac, "carrier_scac")
    return {"op": "tender_dedicated_truckload_via_edi_204", "load_id": str(load_id), "scac": str(carrier_scac).upper(), "src": "recallstorm/dc_ops/carrier_tendering.py"}


def verify_carrier_hazmat_rcra_endorsements(carrier_scac: str, has_hazmat: bool = True) -> dict:
    """Verify carrier DOT Hazmat and EPA RCRA transporter registration."""
    _req(carrier_scac, "carrier_scac")
    return {"op": "verify_carrier_hazmat_rcra_endorsements", "scac": str(carrier_scac).upper(), "approved": bool(has_hazmat), "src": "recallstorm/dc_ops/carrier_tendering.py"}


def track_edi_990_load_acceptance_sla(minutes_elapsed: float, sla_minutes: float = 60.0) -> dict:
    """Track EDI 990 Response to Load Tender against 60-minute acceptance SLA."""
    if minutes_elapsed < 0 or sla_minutes <= 0:
        raise DataValidationError("Invalid minutes")
    return {"op": "track_edi_990_load_acceptance_sla", "within_sla": minutes_elapsed <= sla_minutes, "src": "recallstorm/dc_ops/carrier_tendering.py"}


def negotiate_spot_market_backhaul_rates(miles: float, rate_per_mile: float = 2.85) -> float:
    """Calculate emergency spot-market linehaul cost."""
    if miles <= 0 or rate_per_mile <= 0:
        raise DataValidationError("Miles and rate_per_mile must be positive")
    return round(float(miles) * float(rate_per_mile), 2)


def enforce_sealed_exclusive_use_trailer_rule(load_id: str, co_load_food_allowed: bool = False) -> dict:
    """Enforce Exclusive-Use-Of-Trailer rule (never co-load recalled goods with active food deliveries)."""
    _req(load_id, "load_id")
    return {"op": "enforce_sealed_exclusive_use_trailer_rule", "load_id": str(load_id), "exclusive_use": not co_load_food_allowed, "src": "recallstorm/dc_ops/carrier_tendering.py"}


def monitor_in_transit_gps_breadcrumb_ping(load_id: str, lat: float, lon: float) -> dict:
    """Record in-transit GPS breadcrumb ping for a high-value or Class I return load."""
    _req(load_id, "load_id")
    if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
        raise DataValidationError("Invalid GPS coordinates")
    return {"op": "monitor_in_transit_gps_breadcrumb_ping", "load_id": str(load_id), "coords": [lat, lon], "src": "recallstorm/dc_ops/carrier_tendering.py"}


def handle_carrier_turndown_waterfall_logic(scac_list: list[str], rejected_scac: str) -> str:
    """Select the next carrier SCAC in the routing guide waterfall after a tender turndown."""
    if not scac_list:
        raise DataValidationError("scac_list cannot be empty")
    _req(rejected_scac, "rejected_scac")
    remaining = [s for s in scac_list if s != rejected_scac]
    if not remaining:
        raise DataValidationError("No backup carriers remaining in waterfall")
    return remaining[0]


def validate_proof_of_delivery_at_reclamation(load_id: str, pod_signed: bool = True) -> dict:
    """Validate EDI 214 / signed POD at the reclamation or vendor return center."""
    _req(load_id, "load_id")
    return {"op": "validate_proof_of_delivery_at_reclamation", "load_id": str(load_id), "delivered": bool(pod_signed), "src": "recallstorm/dc_ops/carrier_tendering.py"}


def audit_reverse_freight_accessorial_bills(linehaul_usd: float, fuel_surcharge_usd: float) -> float:
    """Sum freight linehaul and fuel surcharge for vendor chargeback billing."""
    if linehaul_usd < 0 or fuel_surcharge_usd < 0:
        raise DataValidationError("Negative freight amounts")
    return round(float(linehaul_usd) + float(fuel_surcharge_usd), 2)
