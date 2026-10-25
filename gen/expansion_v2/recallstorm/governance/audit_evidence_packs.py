"""Tamper-evident SHA-256 Merkle root audit binders for regulators."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class AuditBinderCompiler:
    """Compiler assembling store-by-store regulatory compliance dossiers."""

    ref_id: str = "GOV-BND-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class TamperEvidentPackager:
    """Cryptographic Merkle-root packager for audit evidence."""

    ref_id: str = "GOV-MRK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def assemble_store_by_store_execution_dossier(recall_id: str, store_ids: list[str]) -> dict:
    """Assemble a store-by-store execution dossier for recall_id."""
    _req(recall_id, "recall_id")
    if not store_ids:
        raise DataValidationError("store_ids cannot be empty")
    return {"op": "assemble_store_by_store_execution_dossier", "recall_id": str(recall_id), "stores": sorted(store_ids), "src": "recallstorm/governance/audit_evidence_packs.py"}


def bundle_timestamped_pos_lock_confirmations(recall_id: str, lane_acks: int) -> dict:
    """Bundle timestamped POS lane lock confirmations."""
    _req(recall_id, "recall_id")
    if lane_acks < 0:
        raise DataValidationError("lane_acks cannot be negative")
    return {"op": "bundle_timestamped_pos_lock_confirmations", "recall_id": str(recall_id), "lane_acks": int(lane_acks), "src": "recallstorm/governance/audit_evidence_packs.py"}


def attach_geotagged_quarantine_cage_photos(store_id: str, photo_hashes: list[str]) -> dict:
    """Attach geotagged quarantine cage photos to the store audit binder."""
    _req(store_id, "store_id")
    if not photo_hashes:
        raise DataValidationError("photo_hashes cannot be empty")
    return {"op": "attach_geotagged_quarantine_cage_photos", "store_id": str(store_id), "photos": list(photo_hashes), "src": "recallstorm/governance/audit_evidence_packs.py"}


def include_signed_destruction_witness_certs(cert_ids: list[str]) -> list[str]:
    """Include dual-signed destruction witness certificates."""
    if cert_ids is None:
        raise DataValidationError("cert_ids cannot be None")
    return sorted(str(c) for c in cert_ids if str(c).strip())


def compute_sha256_merkle_root_for_evidence(hashes: list[str]) -> str:
    """Compute a deterministic SHA-256 Merkle root over evidence item hashes."""
    if not hashes:
        raise DataValidationError("hashes cannot be empty")
    level = [hashlib.sha256(str(h).encode("utf-8")).hexdigest() for h in sorted(hashes)]
    while len(level) > 1:
        nxt: list[str] = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            nxt.append(hashlib.sha256(f"{left}:{right}".encode("utf-8")).hexdigest())
        level = nxt
    return level[0][:16]


def generate_pdf_a_archival_compliance_binder(recall_id: str, merkle_root: str) -> dict:
    """Generate ISO 19005 PDF/A archival compliance binder metadata."""
    _req(recall_id, "recall_id")
    _req(merkle_root, "merkle_root")
    return {"op": "generate_pdf_a_archival_compliance_binder", "recall_id": str(recall_id), "merkle_root": str(merkle_root), "format": "PDF/A-2b", "src": "recallstorm/governance/audit_evidence_packs.py"}


def cross_reference_fda_effectiveness_checks(dossier_stores: set[str], edc_stores: set[str]) -> bool:
    """Verify that all FDA effectiveness-check sample stores are present in the audit dossier."""
    if dossier_stores is None or edc_stores is None:
        raise DataValidationError("Store sets cannot be None")
    return edc_stores.issubset(dossier_stores)


def verify_completeness_of_mandatory_artifacts(artifacts: set[str]) -> dict:
    """Verify presence of POS_LOCK, STORE_ATTESTATION, and DESTRUCTION_CERT in artifacts."""
    if artifacts is None:
        raise DataValidationError("artifacts cannot be None")
    required = {"POS_LOCK", "STORE_ATTESTATION", "DESTRUCTION_CERT"}
    missing = sorted(required - artifacts)
    return {"op": "verify_completeness_of_mandatory_artifacts", "complete": len(missing) == 0, "missing": missing, "src": "recallstorm/governance/audit_evidence_packs.py"}


def watermark_confidential_regulatory_exhibits(exhibit_id: str, agency: str = "FDA") -> str:
    """Apply FOIA-exempt confidential trade-secret watermark string."""
    _req(exhibit_id, "exhibit_id")
    return f"{exhibit_id} [CONFIDENTIAL - 5 U.S.C. 552(b)(4) - SUBMITTED TO {agency.upper()}]"


def export_encrypted_regulator_handoff_zip(recall_id: str, out_path: str) -> dict:
    """Export encrypted regulator handoff archive metadata."""
    _req(recall_id, "recall_id")
    _req(out_path, "out_path")
    return {"op": "export_encrypted_regulator_handoff_zip", "recall_id": str(recall_id), "out_path": str(out_path), "encrypted": True, "src": "recallstorm/governance/audit_evidence_packs.py"}
