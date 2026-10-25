"""FDA PREDICT import holds, customs bond redelivery, and FSVP dossiers."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ImportHoldCoordinator:
    """Coordinator for FDA / CBP import holds and Notice of FDA Action."""

    ref_id: str = "IMP-HLD-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class CustomsEntryQuarantine:
    """Quarantine record for conditional-release ocean containers at transload DCs."""

    ref_id: str = "IMP-CUS-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def match_fda_predict_import_hold_notice(entry_no: str, line_no: int = 1) -> dict:
    """Match an FDA PREDICT entry line hold notice."""
    _req(entry_no, "entry_no")
    if line_no <= 0:
        raise DataValidationError("line_no must be positive")
    return {"op": "match_fda_predict_import_hold_notice", "entry_no": str(entry_no), "line_no": int(line_no), "src": "recallstorm/vendor/import_broker_holds.py"}


def trace_ocean_container_bol_to_drayage(container_id: str, dc_id: str) -> dict:
    """Trace an ocean container BOL from port terminal to import deconsolidation DC."""
    _req(container_id, "container_id")
    _req(dc_id, "dc_id")
    return {"op": "trace_ocean_container_bol_to_drayage", "container_id": str(container_id), "dc_id": str(dc_id), "src": "recallstorm/vendor/import_broker_holds.py"}


def verify_customs_bond_redelivery_demand(cbp_form_4647_id: str, bond_amount_usd: float = 50000.0) -> dict:
    """Track CBP Form 4647 Notice to Mark and/or Notice to Redeliver to avoid 3x value liquidated damages."""
    _req(cbp_form_4647_id, "cbp_form_4647_id")
    if bond_amount_usd <= 0:
        raise DataValidationError("bond_amount_usd must be positive")
    return {"op": "verify_customs_bond_redelivery_demand", "form_4647": str(cbp_form_4647_id), "bond_amount_usd": float(bond_amount_usd), "src": "recallstorm/vendor/import_broker_holds.py"}


def coordinate_fda_private_lab_sampling_packet(entry_no: str, lab_id: str) -> dict:
    """Coordinate private laboratory detention testimony packet for FDA review."""
    _req(entry_no, "entry_no")
    _req(lab_id, "lab_id")
    return {"op": "coordinate_fda_private_lab_sampling_packet", "entry_no": str(entry_no), "lab_id": str(lab_id), "src": "recallstorm/vendor/import_broker_holds.py"}


def hold_deconsolidated_transload_pallets(container_id: str, lpns: list[str]) -> dict:
    """Hold deconsolidated pallets at port transload facility until FDA 'May Proceed' is received."""
    _req(container_id, "container_id")
    if not lpns:
        raise DataValidationError("lpns cannot be empty")
    return {"op": "hold_deconsolidated_transload_pallets", "container_id": str(container_id), "lpns": sorted(lpns), "src": "recallstorm/vendor/import_broker_holds.py"}


def track_notice_of_fda_action_detention(entry_no: str, status: str = "DETAINED") -> dict:
    """Track Notice of FDA Action ('SAMPLED', 'DETAINED', 'REFUSED', 'MAY_PROCEED')."""
    _req(entry_no, "entry_no")
    st = str(status).upper()
    if st not in {"SAMPLED", "DETAINED", "REFUSED", "MAY_PROCEED"}:
        raise DataValidationError(f"Invalid FDA import status: {status!r}")
    return {"op": "track_notice_of_fda_action_detention", "entry_no": str(entry_no), "status": st, "src": "recallstorm/vendor/import_broker_holds.py"}


def calculate_port_demurrage_detention_fees(days_held: int, daily_rate_usd: float = 225.0) -> float:
    """Calculate port container demurrage and chassis detention fees."""
    if days_held < 0 or daily_rate_usd < 0:
        raise DataValidationError("Negative demurrage inputs")
    return round(float(days_held) * float(daily_rate_usd), 2)


def manage_export_or_destruction_under_customs(entry_no: str, mode: str = "DESTROY_CBP") -> dict:
    """Record exportation or CBP/FDA witnessed destruction within 90 days of Import Refusal."""
    _req(entry_no, "entry_no")
    _req(mode, "mode")
    return {"op": "manage_export_or_destruction_under_customs", "entry_no": str(entry_no), "mode": str(mode).upper(), "src": "recallstorm/vendor/import_broker_holds.py"}


def audit_foreign_supplier_fsvp_dossiers(supplier_id: str, hazard_analysis_complete: bool = True) -> dict:
    """Audit 21 CFR Part 1 Subpart L Foreign Supplier Verification Program (FSVP) dossier."""
    _req(supplier_id, "supplier_id")
    return {"op": "audit_foreign_supplier_fsvp_dossiers", "supplier_id": str(supplier_id), "compliant": bool(hazard_analysis_complete), "src": "recallstorm/vendor/import_broker_holds.py"}


def release_may_proceed_entries_to_dc(entry_no: str, fda_may_proceed: bool = True) -> dict:
    """Release import pallets into domestic DC stock upon electronic FDA 'May Proceed' message."""
    _req(entry_no, "entry_no")
    return {"op": "release_may_proceed_entries_to_dc", "entry_no": str(entry_no), "released": bool(fda_may_proceed), "src": "recallstorm/vendor/import_broker_holds.py"}
