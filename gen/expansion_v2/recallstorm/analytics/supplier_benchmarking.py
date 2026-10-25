"""Peer supplier recall rate comparison and COPQ ranking."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class PeerSupplierComparator:
    """Comparator benchmarking suppliers within the same product category."""

    ref_id: str = "BMK-PEER-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class CategorySafetyRanker:
    """Ranker scoring suppliers by Cost of Poor Quality (COPQ) and EPCIS adoption."""

    ref_id: str = "BMK-RNK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def normalize_recalls_per_million_cases_shipped(recalls: int, cases_shipped: int) -> float:
    """Compute recalls per 1,000,000 cases shipped."""
    if recalls < 0 or cases_shipped <= 0:
        raise DataValidationError("Invalid recalls or cases_shipped")
    return round((recalls / cases_shipped) * 1_000_000.0, 4)


def compare_private_label_vs_national_brand_rate(pl_rate: float, nb_rate: float) -> dict:
    """Compare private-label recall rate against national-brand recall rate."""
    if pl_rate < 0 or nb_rate < 0:
        raise DataValidationError("Negative rates")
    return {"op": "compare_private_label_vs_national_brand_rate", "pl_safer": pl_rate <= nb_rate, "delta": round(pl_rate - nb_rate, 4), "src": "recallstorm/analytics/supplier_benchmarking.py"}


def benchmark_traceability_epcis_adoption_rate(epcis_asns: int, total_asns: int) -> float:
    """Calculate percentage of supplier ASNs containing valid GS1 EPCIS lot data."""
    if epcis_asns < 0 or total_asns <= 0 or epcis_asns > total_asns:
        raise DataValidationError("Invalid ASN counts")
    return round((epcis_asns / total_asns) * 100.0, 2)


def score_vendor_responsiveness_during_drills(response_mins: float, target_mins: float = 30.0) -> float:
    """Score supplier mock-recall responsiveness in [0.0, 100.0]."""
    if response_mins < 0 or target_mins <= 0:
        raise DataValidationError("Invalid minutes")
    if response_mins <= target_mins:
        return 100.0
    return round(max(0.0, 100.0 - (response_mins - target_mins) * 2.0), 2)


def analyze_coa_rejection_rate_by_country_origin(rejections: dict[str, int]) -> list[str]:
    """Order countries of origin by COA rejection count descending."""
    if rejections is None:
        raise DataValidationError("rejections cannot be None")
    return [k for k, _ in sorted(rejections.items(), key=lambda x: (-int(x[1]), str(x[0])))]


def cluster_vendors_by_shared_co_packer_risk(vendor_to_plant: dict[str, str]) -> dict[str, list[str]]:
    """Group vendor IDs that share the same underlying co-packer facility."""
    if vendor_to_plant is None:
        raise DataValidationError("vendor_to_plant cannot be None")
    by_plant: dict[str, list[str]] = {}
    for v, p in sorted(vendor_to_plant.items()):
        by_plant.setdefault(str(p), []).append(str(v))
    return by_plant


def identify_single_source_vulnerable_categories(suppliers_per_sku: dict[str, int]) -> list[str]:
    """Return sorted SKU IDs that have only 1 approved supplier and no substitute."""
    if suppliers_per_sku is None:
        raise DataValidationError("suppliers_per_sku cannot be None")
    return sorted(sku for sku, cnt in suppliers_per_sku.items() if int(cnt) <= 1)


def calculate_cost_of_poor_quality_by_supplier(recall_costs_usd: float, annual_cogs_usd: float) -> float:
    """Compute supplier Cost of Poor Quality (COPQ) as a percentage of annual COGS."""
    if recall_costs_usd < 0 or annual_cogs_usd <= 0:
        raise DataValidationError("Invalid COPQ inputs")
    return round((recall_costs_usd / annual_cogs_usd) * 100.0, 4)


def generate_quarterly_qbr_safety_slide_data(vendor_id: str, copq_pct: float) -> dict:
    """Generate supplier Quarterly Business Review (QBR) food safety summary."""
    _req(vendor_id, "vendor_id")
    if copq_pct < 0:
        raise DataValidationError("copq_pct cannot be negative")
    return {"op": "generate_quarterly_qbr_safety_slide_data", "vendor_id": str(vendor_id), "copq_pct": float(copq_pct), "src": "recallstorm/analytics/supplier_benchmarking.py"}


def rank_vendors_for_preferred_partner_status(scores: dict[str, float], min_score: float = 90.0) -> list[str]:
    """Return vendor IDs meeting min_score ordered highest first."""
    if scores is None:
        raise DataValidationError("scores cannot be None")
    qualified = [(v, s) for v, s in scores.items() if float(s) >= min_score]
    qualified.sort(key=lambda x: (-float(x[1]), str(x[0])))
    return [v for v, _ in qualified]
