"""ICMSF microbiological sampling plans and WGS SNP distance matching."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class MicrobiologicalSamplingPlan:
    """ICMSF 2-class or 3-class microbiological attribute sampling plan."""

    ref_id: str = "ICMSF-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class IcmsfAcceptanceCriteria:
    """ICMSF parameters (n, c, m, M) for lot acceptance."""

    ref_id: str = "ICMSF-CRIT"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def calculate_icmsf_case_class_plan(case_number: int = 10) -> dict:
    """Return ICMSF sample size 'n' and maximum allowable positives 'c' for case_number (1..15)."""
    if not isinstance(case_number, int) or not (1 <= case_number <= 15):
        raise DataValidationError("ICMSF case_number must be in 1..15")
    if case_number >= 10:
        n = 5 if case_number == 10 else (15 if case_number <= 12 else 60)
        return {"case": case_number, "n": n, "c": 0}
    return {"case": case_number, "n": 5, "c": 2}


def assign_composite_sub_sample_units(total_subsamples: int = 60, pool_size: int = 15) -> int:
    """Calculate number of wet-pooled composite lab tests from total_subsamples and pool_size."""
    if total_subsamples <= 0 or pool_size <= 0:
        raise DataValidationError("Invalid subsample or pool size")
    return max(1, total_subsamples // pool_size)


def generate_aseptic_collection_protocol(sku_id: str, sample_g: int = 375) -> dict:
    """Generate aseptic sample collection instructions."""
    _req(sku_id, "sku_id")
    if sample_g <= 0:
        raise DataValidationError("sample_g must be positive")
    return {"op": "generate_aseptic_collection_protocol", "sku_id": str(sku_id), "sample_g": int(sample_g), "src": "recallstorm/food_safety/sampling_plans.py"}


def track_chain_of_custody_seal(seal_id: str, intact: bool = True) -> dict:
    """Verify tamper-evident chain-of-custody seal on lab samples."""
    _req(seal_id, "seal_id")
    return {"op": "track_chain_of_custody_seal", "seal_id": str(seal_id), "valid": bool(intact), "src": "recallstorm/food_safety/sampling_plans.py"}


def parse_pcr_presumptive_positive(sample_id: str, ct_value: float = 28.0) -> dict:
    """Evaluate real-time PCR cycle threshold (Ct < 37.0 indicates presumptive positive)."""
    _req(sample_id, "sample_id")
    if ct_value <= 0:
        raise DataValidationError("ct_value must be positive")
    return {"op": "parse_pcr_presumptive_positive", "sample_id": str(sample_id), "presumptive_positive": ct_value < 37.0, "src": "recallstorm/food_safety/sampling_plans.py"}


def evaluate_wgs_snp_distance_match(snp_distance: int, max_snps: int = 10) -> dict:
    """Evaluate Whole Genome Sequencing (WGS) SNP distance against clinical outbreak isolate."""
    if not isinstance(snp_distance, int) or snp_distance < 0 or max_snps < 0:
        raise DataValidationError("Invalid snp_distance")
    return {"op": "evaluate_wgs_snp_distance_match", "clonal_match": snp_distance <= max_snps, "snp_distance": snp_distance, "src": "recallstorm/food_safety/sampling_plans.py"}


def manage_hold_and_test_release(lot_id: str, negatives: int, required_n: int = 60) -> dict:
    """Authorize test-and-release only if all required_n subsamples tested negative."""
    _req(lot_id, "lot_id")
    if negatives < 0 or required_n <= 0:
        raise DataValidationError("Invalid sample counts")
    return {"op": "manage_hold_and_test_release", "lot_id": str(lot_id), "release_authorized": negatives >= required_n, "src": "recallstorm/food_safety/sampling_plans.py"}


def flag_lab_turnaround_sla_breach(hours_elapsed: float, sla_hours: float = 72.0) -> dict:
    """Flag microbiological lab testing exceeding SLA turnaround time."""
    if hours_elapsed < 0 or sla_hours <= 0:
        raise DataValidationError("Invalid hours")
    return {"op": "flag_lab_turnaround_sla_breach", "breached": hours_elapsed > sla_hours, "src": "recallstorm/food_safety/sampling_plans.py"}


def build_cpsc_destructive_test_lot(sku_id: str, units: int = 12) -> dict:
    """Build a CPSC destructive mechanical/chemical test sample lot."""
    _req(sku_id, "sku_id")
    if units <= 0:
        raise DataValidationError("units must be positive")
    return {"op": "build_cpsc_destructive_test_lot", "sku_id": str(sku_id), "units": int(units), "src": "recallstorm/food_safety/sampling_plans.py"}


def archive_certificate_of_analysis(coa_id: str, lot_id: str) -> dict:
    """Archive a verified Certificate of Analysis (COA)."""
    _req(coa_id, "coa_id")
    _req(lot_id, "lot_id")
    return {"op": "archive_certificate_of_analysis", "coa_id": str(coa_id), "lot_id": str(lot_id), "src": "recallstorm/food_safety/sampling_plans.py"}
