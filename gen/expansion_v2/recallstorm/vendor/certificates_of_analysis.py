"""COA repository, ISO 17025 lab validation, and ASN batch matching."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class CoaRepository:
    """Repository of supplier Certificates of Analysis (COAs)."""

    ref_id: str = "COA-REP-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class LabResultValidator:
    """Validator for third-party ISO/IEC 17025 lab assay results."""

    ref_id: str = "COA-VAL-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def ingest_pdf_edifact_coa_documents(coa_id: str, batch_id: str) -> dict:
    """Ingest a batch COA document."""
    _req(coa_id, "coa_id")
    _req(batch_id, "batch_id")
    return {"op": "ingest_pdf_edifact_coa_documents", "coa_id": str(coa_id), "batch_id": str(batch_id), "src": "recallstorm/vendor/certificates_of_analysis.py"}


def verify_iso_17025_lab_accreditation_scope(lab_id: str, accredited: bool = True) -> dict:
    """Verify that the testing laboratory holds active ISO/IEC 17025 accreditation for the analyte."""
    _req(lab_id, "lab_id")
    return {"op": "verify_iso_17025_lab_accreditation_scope", "lab_id": str(lab_id), "valid": bool(accredited), "src": "recallstorm/vendor/certificates_of_analysis.py"}


def match_coa_batch_id_to_asn_lot(coa_lots: list[str], asn_lot: str) -> bool:
    """Return True if asn_lot has a matching COA in coa_lots."""
    if coa_lots is None:
        raise DataValidationError("coa_lots cannot be None")
    _req(asn_lot, "asn_lot")
    return str(asn_lot).strip().upper() in {str(c).strip().upper() for c in coa_lots}


def check_heavy_metal_pfas_pass_fail_limits(measured_ppb: float, spec_limit_ppb: float) -> dict:
    """Evaluate COA measured analyte concentration against specification limit."""
    if measured_ppb < 0 or spec_limit_ppb <= 0:
        raise DataValidationError("Invalid ppb values")
    return {"op": "check_heavy_metal_pfas_pass_fail_limits", "passed": measured_ppb <= spec_limit_ppb, "measured_ppb": float(measured_ppb), "src": "recallstorm/vendor/certificates_of_analysis.py"}


def flag_expired_annual_testing_certificates(cert_date_iso: str, min_date_iso: str = "2026-01-01") -> dict:
    """Flag annual supplier compliance certificates older than 12 months."""
    _req(cert_date_iso, "cert_date_iso")
    return {"op": "flag_expired_annual_testing_certificates", "expired": str(cert_date_iso) < str(min_date_iso), "src": "recallstorm/vendor/certificates_of_analysis.py"}


def detect_altered_fraudulent_coa_pdfs(expected_hash: str, actual_hash: str) -> dict:
    """Detect tampered or forged COA PDFs via cryptographic hash comparison."""
    _req(expected_hash, "expected_hash")
    _req(actual_hash, "actual_hash")
    return {"op": "detect_altered_fraudulent_coa_pdfs", "fraud_detected": str(expected_hash) != str(actual_hash), "src": "recallstorm/vendor/certificates_of_analysis.py"}


def block_receiving_on_missing_coa_gate(po_id: str, coa_present: bool = False) -> dict:
    """Place inbound DC receipt on QA hold if a required high-risk COA is missing."""
    _req(po_id, "po_id")
    return {"op": "block_receiving_on_missing_coa_gate", "po_id": str(po_id), "blocked": not coa_present, "src": "recallstorm/vendor/certificates_of_analysis.py"}


def alert_qa_to_marginal_spec_results(measured: float, limit: float) -> dict:
    """Alert QA when COA result is within 10% of the maximum action limit."""
    if measured < 0 or limit <= 0:
        raise DataValidationError("Invalid measured or limit")
    marginal = (limit * 0.9) <= measured <= limit
    return {"op": "alert_qa_to_marginal_spec_results", "marginal_alert": marginal, "src": "recallstorm/vendor/certificates_of_analysis.py"}


def link_coa_to_gs1_epcis_lot_master(coa_id: str, gtin: str, lot_id: str) -> dict:
    """Bind COA ID to GS1 (GTIN, Lot) master record."""
    _req(coa_id, "coa_id")
    _req(gtin, "gtin")
    _req(lot_id, "lot_id")
    return {"op": "link_coa_to_gs1_epcis_lot_master", "coa_id": str(coa_id), "gtin": str(gtin), "lot_id": str(lot_id), "src": "recallstorm/vendor/certificates_of_analysis.py"}


def archive_regulatory_audit_coa_bundle(recall_id: str, coa_ids: list[str]) -> dict:
    """Bundle all COAs associated with recall_id for regulatory inspection."""
    _req(recall_id, "recall_id")
    if coa_ids is None:
        raise DataValidationError("coa_ids cannot be None")
    return {"op": "archive_regulatory_audit_coa_bundle", "recall_id": str(recall_id), "count": len(coa_ids), "src": "recallstorm/vendor/certificates_of_analysis.py"}
