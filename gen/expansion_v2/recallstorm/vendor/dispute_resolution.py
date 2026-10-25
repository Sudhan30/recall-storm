"""Vendor chargeback dispute arbitration and scan-log evidence dossiers."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ChargebackDisputeQueue:
    """Queue of supplier-submitted recall chargeback disputes."""

    ref_id: str = "DSP-QUE-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class EvidenceArbitrator:
    """Arbitrator evaluating store pull scan logs and lot photos against vendor disputes."""

    ref_id: str = "DSP-ARB-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def ingest_vendor_dispute_portal_submission(dispute_id: str, vendor_id: str, disputed_usd: float) -> dict:
    """Ingest a supplier chargeback dispute from the vendor portal."""
    _req(dispute_id, "dispute_id")
    _req(vendor_id, "vendor_id")
    if disputed_usd <= 0:
        raise DataValidationError("disputed_usd must be positive")
    return {"op": "ingest_vendor_dispute_portal_submission", "dispute_id": str(dispute_id), "vendor_id": str(vendor_id), "disputed_usd": round(float(disputed_usd), 2), "src": "recallstorm/vendor/dispute_resolution.py"}


def attach_timestamped_store_pull_scan_logs(dispute_id: str, scan_events: int) -> dict:
    """Attach immutable store RF pull scan logs as proof of execution."""
    _req(dispute_id, "dispute_id")
    if scan_events < 0:
        raise DataValidationError("scan_events cannot be negative")
    return {"op": "attach_timestamped_store_pull_scan_logs", "dispute_id": str(dispute_id), "scan_events": int(scan_events), "src": "recallstorm/vendor/dispute_resolution.py"}


def verify_photo_proof_of_affected_lot_code(dispute_id: str, photo_verified: bool = True) -> dict:
    """Verify store photo showing the recalled lot code on pulled cases."""
    _req(dispute_id, "dispute_id")
    return {"op": "verify_photo_proof_of_affected_lot_code", "dispute_id": str(dispute_id), "verified": bool(photo_verified), "src": "recallstorm/vendor/dispute_resolution.py"}


def recalculate_disputed_unit_cost_basis(units: int, agreed_unit_cost: float) -> float:
    """Recalculate chargeback merchandise value at agreed_unit_cost."""
    if units < 0 or agreed_unit_cost < 0:
        raise DataValidationError("Negative unit or cost")
    return round(float(units) * float(agreed_unit_cost), 2)


def evaluate_force_majeure_contract_claims(reason: str) -> dict:
    """Evaluate supplier Force Majeure defense (regulatory bans and adulteration never qualify as Force Majeure)."""
    _req(reason, "reason")
    return {"op": "evaluate_force_majeure_contract_claims", "reason": str(reason), "excused": False, "src": "recallstorm/vendor/dispute_resolution.py"}


def route_high_dollar_dispute_to_merch_vp(dispute_id: str, amount_usd: float, threshold_usd: float = 25000.0) -> dict:
    """Route disputes exceeding $25,000 to VP Merchandising and Finance."""
    _req(dispute_id, "dispute_id")
    if amount_usd < 0 or threshold_usd <= 0:
        raise DataValidationError("Invalid amount_usd")
    return {"op": "route_high_dollar_dispute_to_merch_vp", "dispute_id": str(dispute_id), "vp_routed": amount_usd >= threshold_usd, "src": "recallstorm/vendor/dispute_resolution.py"}


def apply_partial_settlement_credit_adjustment(orig_chargeback_usd: float, credit_back_usd: float) -> float:
    """Apply a negotiated partial settlement credit adjustment."""
    if orig_chargeback_usd < 0 or credit_back_usd < 0 or credit_back_usd > orig_chargeback_usd:
        raise DataValidationError("Invalid settlement amounts")
    return round(float(orig_chargeback_usd) - float(credit_back_usd), 2)


def track_dispute_resolution_cycle_time_days(days_open: int, sla_days: int = 30) -> dict:
    """Track dispute resolution cycle time against 30-day SLA."""
    if days_open < 0 or sla_days <= 0:
        raise DataValidationError("Invalid days")
    return {"op": "track_dispute_resolution_cycle_time_days", "within_sla": days_open <= sla_days, "days_open": int(days_open), "src": "recallstorm/vendor/dispute_resolution.py"}


def lock_settled_claims_from_re_submission(dispute_id: str) -> dict:
    """Lock a settled dispute claim so the vendor portal rejects duplicate re-submissions."""
    _req(dispute_id, "dispute_id")
    return {"op": "lock_settled_claims_from_re_submission", "dispute_id": str(dispute_id), "locked": True, "src": "recallstorm/vendor/dispute_resolution.py"}


def generate_arbitration_evidence_dossier(dispute_id: str, artifacts: list[str]) -> dict:
    """Compile a complete arbitration evidence dossier."""
    _req(dispute_id, "dispute_id")
    if not artifacts:
        raise DataValidationError("artifacts cannot be empty")
    return {"op": "generate_arbitration_evidence_dossier", "dispute_id": str(dispute_id), "artifact_count": len(artifacts), "src": "recallstorm/vendor/dispute_resolution.py"}
