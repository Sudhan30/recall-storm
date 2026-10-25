"""Supplier recall directives, COA demands, and crisis bridge calls."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class SupplierRecallDirective:
    """Formal notice of quarantine and compliance demand sent to a vendor."""

    ref_id: str = "VND-DIR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class VendorComplianceDemand:
    """Demand for COA, root-cause CAPA, and distribution manifests."""

    ref_id: str = "VND-DEM-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def issue_formal_notice_of_quarantine(vendor_id: str, sku_ids: list[str]) -> dict:
    """Issue a formal notice of inventory quarantine to vendor_id."""
    _req(vendor_id, "vendor_id")
    if not sku_ids:
        raise DataValidationError("sku_ids cannot be empty")
    return {"op": "issue_formal_notice_of_quarantine", "vendor_id": str(vendor_id), "skus": sorted(sku_ids), "src": "recallstorm/comms/vendor_notices.py"}


def request_immediate_coa_and_root_cause(vendor_id: str, lot_id: str, sla_hours: int = 4) -> dict:
    """Demand batch COA and preliminary 5-Why root-cause report within sla_hours."""
    _req(vendor_id, "vendor_id")
    _req(lot_id, "lot_id")
    if sla_hours <= 0:
        raise DataValidationError("sla_hours must be positive")
    return {"op": "request_immediate_coa_and_root_cause", "vendor_id": str(vendor_id), "lot_id": str(lot_id), "sla_hours": int(sla_hours), "src": "recallstorm/comms/vendor_notices.py"}


def demand_lot_distribution_manifest_csv(vendor_id: str, recall_id: str) -> dict:
    """Demand complete EDI/CSV lot-to-DC shipment manifest from vendor_id."""
    _req(vendor_id, "vendor_id")
    _req(recall_id, "recall_id")
    return {"op": "demand_lot_distribution_manifest_csv", "vendor_id": str(vendor_id), "recall_id": str(recall_id), "src": "recallstorm/comms/vendor_notices.py"}


def notify_vendor_of_pos_lock_activation(vendor_id: str, sku_id: str) -> dict:
    """Notify supplier that POS checkout hard-lock has been activated on sku_id."""
    _req(vendor_id, "vendor_id")
    _req(sku_id, "sku_id")
    return {"op": "notify_vendor_of_pos_lock_activation", "vendor_id": str(vendor_id), "sku_id": str(sku_id), "src": "recallstorm/comms/vendor_notices.py"}


def transmit_estimated_chargeback_schedule(vendor_id: str, estimated_usd: float) -> dict:
    """Transmit preliminary recall execution and product write-off chargeback estimate."""
    _req(vendor_id, "vendor_id")
    if estimated_usd < 0:
        raise DataValidationError("estimated_usd cannot be negative")
    return {"op": "transmit_estimated_chargeback_schedule", "vendor_id": str(vendor_id), "estimated_usd": round(float(estimated_usd), 2), "src": "recallstorm/comms/vendor_notices.py"}


def require_indemnification_hold_harmless(vendor_id: str, recall_id: str) -> dict:
    """Tender formal Master Supply Agreement indemnification notice."""
    _req(vendor_id, "vendor_id")
    _req(recall_id, "recall_id")
    return {"op": "require_indemnification_hold_harmless", "vendor_id": str(vendor_id), "recall_id": str(recall_id), "src": "recallstorm/comms/vendor_notices.py"}


def escalate_unresponsive_vendor_contacts(vendor_id: str, hours_unanswered: float) -> dict:
    """Escalate to VP Merchandising and Legal when emergency vendor contact is unresponsive (> 2.0h)."""
    _req(vendor_id, "vendor_id")
    if hours_unanswered < 0:
        raise DataValidationError("hours_unanswered cannot be negative")
    return {"op": "escalate_unresponsive_vendor_contacts", "vendor_id": str(vendor_id), "escalated": hours_unanswered > 2.0, "src": "recallstorm/comms/vendor_notices.py"}


def track_vendor_portal_document_uploads(vendor_id: str, uploaded_docs: list[str]) -> dict:
    """Track mandatory recall documents uploaded to supplier portal."""
    _req(vendor_id, "vendor_id")
    if uploaded_docs is None:
        raise DataValidationError("uploaded_docs cannot be None")
    return {"op": "track_vendor_portal_document_uploads", "vendor_id": str(vendor_id), "doc_count": len(uploaded_docs), "src": "recallstorm/comms/vendor_notices.py"}


def schedule_joint_crisis_bridge_call(vendor_id: str, start_iso: str) -> dict:
    """Schedule an emergency joint QA/Supply-Chain crisis bridge call."""
    _req(vendor_id, "vendor_id")
    _req(start_iso, "start_iso")
    return {"op": "schedule_joint_crisis_bridge_call", "vendor_id": str(vendor_id), "start_iso": str(start_iso), "src": "recallstorm/comms/vendor_notices.py"}


def log_vendor_disposition_instructions(vendor_id: str, disposition: str = "DESTROY_AT_STORE") -> dict:
    """Log written supplier disposition instructions ('DESTROY_AT_STORE', 'DESTROY_AT_DC', or 'RETURN_TO_VENDOR')."""
    _req(vendor_id, "vendor_id")
    d = str(disposition).upper()
    if d not in {"DESTROY_AT_STORE", "DESTROY_AT_DC", "RETURN_TO_VENDOR"}:
        raise DataValidationError(f"Invalid disposition: {disposition!r}")
    return {"op": "log_vendor_disposition_instructions", "vendor_id": str(vendor_id), "disposition": d, "src": "recallstorm/comms/vendor_notices.py"}
