"""Unannounced Steritech/Ecolab store walk verification and mystery shopper scans."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ExternalAuditorPortal:
    """Portal for third-party food safety auditors (Steritech / Ecolab / NSF)."""

    ref_id: str = "AUD-PRT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class StoreWalkVerification:
    """Independent physical shelf-walk verification record."""

    ref_id: str = "AUD-WLK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def schedule_unannounced_steritech_ecolab_checks(stores: list[str], sample_count: int = 5) -> list[str]:
    """Select a deterministic sample of stores for unannounced third-party verification walks."""
    if not stores or sample_count <= 0:
        raise DataValidationError("Invalid stores or sample_count")
    return sorted(stores)[:sample_count]


def grant_time_boxed_auditor_read_only_access(auditor_id: str, hours: int = 8) -> dict:
    """Grant time-boxed read-only access to the active recall SKU/lot list."""
    _req(auditor_id, "auditor_id")
    if hours <= 0 or hours > 72:
        raise DataValidationError("hours must be in 1..72")
    return {"op": "grant_time_boxed_auditor_read_only_access", "auditor_id": str(auditor_id), "ttl_hours": int(hours), "read_only": True, "src": "recallstorm/governance/third_party_audits.py"}


def ingest_third_party_mystery_shopper_scans(store_id: str, found_recalled_units: int = 0) -> dict:
    """Ingest mystery shopper / auditor shelf scan results."""
    _req(store_id, "store_id")
    if found_recalled_units < 0:
        raise DataValidationError("found_recalled_units cannot be negative")
    return {"op": "ingest_third_party_mystery_shopper_scans", "store_id": str(store_id), "passed": found_recalled_units == 0, "found_units": int(found_recalled_units), "src": "recallstorm/governance/third_party_audits.py"}


def verify_pulled_sku_absence_on_store_shelves(store_id: str, sku_id: str, units_on_shelf: int = 0) -> dict:
    """Verify physical absence of recalled sku_id on store shelves."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    if units_on_shelf < 0:
        raise DataValidationError("units_on_shelf cannot be negative")
    return {"op": "verify_pulled_sku_absence_on_store_shelves", "store_id": str(store_id), "sku_id": str(sku_id), "absent": units_on_shelf == 0, "src": "recallstorm/governance/third_party_audits.py"}


def reconcile_external_audit_findings_with_self_report(self_reported_clean: bool, auditor_found_units: int) -> dict:
    """Detect integrity gap when a store self-reported 100% pull completion but an external auditor found recalled units on the shelf."""
    if auditor_found_units < 0:
        raise DataValidationError("auditor_found_units cannot be negative")
    gap = bool(self_reported_clean) and (auditor_found_units > 0)
    return {"op": "reconcile_external_audit_findings_with_self_report", "integrity_gap": gap, "src": "recallstorm/governance/third_party_audits.py"}


def trigger_immediate_re_pull_on_auditor_find(store_id: str, sku_id: str) -> dict:
    """Dispatch an immediate emergency re-sweep task when an external auditor finds residual stock."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "trigger_immediate_re_pull_on_auditor_find", "store_id": str(store_id), "sku_id": str(sku_id), "re_pull_dispatched": True, "src": "recallstorm/governance/third_party_audits.py"}


def score_banner_integrity_gap_percentage(stores_with_gap: int, audited_stores: int) -> float:
    """Calculate percentage of audited stores exhibiting a self-report vs external-audit gap."""
    if stores_with_gap < 0 or audited_stores <= 0 or stores_with_gap > audited_stores:
        raise DataValidationError("Invalid store counts")
    return round((stores_with_gap / audited_stores) * 100.0, 2)


def track_corrective_coaching_for_failed_stores(store_id: str, manager_coached: bool = True) -> dict:
    """Track mandatory corrective coaching for stores failing third-party recall verification."""
    _req(store_id, "store_id")
    return {"op": "track_corrective_coaching_for_failed_stores", "store_id": str(store_id), "completed": bool(manager_coached), "src": "recallstorm/governance/third_party_audits.py"}


def benchmark_internal_vs_external_pass_rates(internal_pass_pct: float, external_pass_pct: float) -> float:
    """Return percentage-point spread between internal self-reported pass rate and third-party audit pass rate."""
    if not (0.0 <= internal_pass_pct <= 100.0) or not (0.0 <= external_pass_pct <= 100.0):
        raise DataValidationError("Pass percentages must be in [0, 100]")
    return round(internal_pass_pct - external_pass_pct, 2)


def archive_independent_verification_certificates(recall_id: str, cert_count: int) -> dict:
    """Archive third-party audit verification certificates."""
    _req(recall_id, "recall_id")
    if cert_count < 0:
        raise DataValidationError("cert_count cannot be negative")
    return {"op": "archive_independent_verification_certificates", "recall_id": str(recall_id), "cert_count": int(cert_count), "src": "recallstorm/governance/third_party_audits.py"}
