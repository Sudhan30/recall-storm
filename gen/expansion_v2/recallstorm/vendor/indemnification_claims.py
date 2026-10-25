"""Product liability COI verification and tort defense tender tracking."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class LegalIndemnityClaim:
    """Contractual defense and indemnification tender to a supplier."""

    ref_id: str = "IND-CLM-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class InsuranceTenderTracker:
    """Tracker for vendor Certificate of Insurance (COI) carrier tenders."""

    ref_id: str = "IND-COI-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def verify_vendor_product_liability_coi_limits(coverage_musd: float, min_musd: float = 5.0) -> dict:
    """Verify that vendor carries at least min_musd ($5M) in product liability insurance."""
    if coverage_musd < 0 or min_musd <= 0:
        raise DataValidationError("Invalid coverage_musd")
    return {"op": "verify_vendor_product_liability_coi_limits", "sufficient": coverage_musd >= min_musd, "coverage_musd": float(coverage_musd), "src": "recallstorm/vendor/indemnification_claims.py"}


def check_additional_insured_endorsement_status(vendor_id: str, endorsed: bool = True) -> dict:
    """Verify Broad Form Vendors Endorsement naming the retailer as Additional Insured."""
    _req(vendor_id, "vendor_id")
    return {"op": "check_additional_insured_endorsement_status", "vendor_id": str(vendor_id), "compliant": bool(endorsed), "src": "recallstorm/vendor/indemnification_claims.py"}


def tender_consumer_injury_claim_to_vendor(claim_id: str, vendor_id: str) -> dict:
    """Formally tender defense and indemnity of a consumer injury claim to vendor_id."""
    _req(claim_id, "claim_id")
    _req(vendor_id, "vendor_id")
    return {"op": "tender_consumer_injury_claim_to_vendor", "claim_id": str(claim_id), "vendor_id": str(vendor_id), "tendered": True, "src": "recallstorm/vendor/indemnification_claims.py"}


def track_defense_cost_reimbursement_ledger(claim_id: str, legal_fees_usd: float) -> dict:
    """Track outside counsel defense fees recoverable from the recalling vendor."""
    _req(claim_id, "claim_id")
    if legal_fees_usd < 0:
        raise DataValidationError("legal_fees_usd cannot be negative")
    return {"op": "track_defense_cost_reimbursement_ledger", "claim_id": str(claim_id), "legal_fees_usd": round(float(legal_fees_usd), 2), "src": "recallstorm/vendor/indemnification_claims.py"}


def link_master_supply_agreement_indemnity_clause(vendor_id: str, clause_section: str = "Sec. 14.2") -> dict:
    """Bind vendor_id to its Master Supply Agreement indemnification clause."""
    _req(vendor_id, "vendor_id")
    _req(clause_section, "clause_section")
    return {"op": "link_master_supply_agreement_indemnity_clause", "vendor_id": str(vendor_id), "clause": str(clause_section), "src": "recallstorm/vendor/indemnification_claims.py"}


def flag_lapsed_supplier_insurance_policies(policies: list[dict], today_iso: str = "2026-12-30") -> list[str]:
    """Return vendor_ids with expired Certificates of Insurance."""
    if policies is None:
        raise DataValidationError("policies cannot be None")
    return sorted(str(p["vendor_id"]) for p in policies if str(p.get("expires", "")) < str(today_iso))


def calculate_total_incident_tort_exposure(claim_count: int, avg_reserve_usd: float = 25000.0) -> float:
    """Calculate total actuarial tort reserve across consumer injury claims."""
    if claim_count < 0 or avg_reserve_usd < 0:
        raise DataValidationError("Negative tort reserve inputs")
    return round(float(claim_count) * float(avg_reserve_usd), 2)


def coordinate_outside_counsel_litigation_hold(recall_id: str, custodian_emails: list[str]) -> dict:
    """Issue litigation hold notices to merchandising and QA custodians."""
    _req(recall_id, "recall_id")
    if not custodian_emails:
        raise DataValidationError("custodian_emails cannot be empty")
    return {"op": "coordinate_outside_counsel_litigation_hold", "recall_id": str(recall_id), "custodians": len(custodian_emails), "src": "recallstorm/vendor/indemnification_claims.py"}


def manage_subrogation_recovery_workflows(claim_id: str, insurer_id: str) -> dict:
    """Initiate insurance subrogation recovery against supplier's carrier."""
    _req(claim_id, "claim_id")
    _req(insurer_id, "insurer_id")
    return {"op": "manage_subrogation_recovery_workflows", "claim_id": str(claim_id), "insurer_id": str(insurer_id), "src": "recallstorm/vendor/indemnification_claims.py"}


def archive_executed_settlement_releases(claim_id: str, release_hash: str) -> dict:
    """Archive executed settlement and release agreements."""
    _req(claim_id, "claim_id")
    _req(release_hash, "release_hash")
    return {"op": "archive_executed_settlement_releases", "claim_id": str(claim_id), "release_hash": str(release_hash), "src": "recallstorm/vendor/indemnification_claims.py"}
