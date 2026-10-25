"""Unit tests for recallstorm.analytics.supplier_benchmarking."""
from recallstorm.analytics.supplier_benchmarking import (
    CategorySafetyRanker,
    PeerSupplierComparator,
    analyze_coa_rejection_rate_by_country_origin,
    benchmark_traceability_epcis_adoption_rate,
    calculate_cost_of_poor_quality_by_supplier,
    cluster_vendors_by_shared_co_packer_risk,
    compare_private_label_vs_national_brand_rate,
    generate_quarterly_qbr_safety_slide_data,
    identify_single_source_vulnerable_categories,
    normalize_recalls_per_million_cases_shipped,
    rank_vendors_for_preferred_partner_status,
    score_vendor_responsiveness_during_drills,
)


def test_supplier_benchmarking():
    assert PeerSupplierComparator().status == "ACTIVE"
    assert CategorySafetyRanker().status == "ACTIVE"
    assert normalize_recalls_per_million_cases_shipped(2, 500_000) == 4.0
    assert compare_private_label_vs_national_brand_rate(1.0, 2.0)["pl_safer"] is True
    assert benchmark_traceability_epcis_adoption_rate(95, 100) == 95.0
    assert score_vendor_responsiveness_during_drills(20.0, 30.0) == 100.0
    assert analyze_coa_rejection_rate_by_country_origin({"CN": 2, "IN": 5}) == ["IN", "CN"]
    assert cluster_vendors_by_shared_co_packer_risk({"V1": "PLT1", "V2": "PLT1"}) == {"PLT1": ["V1", "V2"]}
    assert identify_single_source_vulnerable_categories({"S1": 1, "S2": 3}) == ["S1"]
    assert calculate_cost_of_poor_quality_by_supplier(10000.0, 1_000_000.0) == 1.0
    assert generate_quarterly_qbr_safety_slide_data("V1", 0.5)["vendor_id"] == "V1"
    assert rank_vendors_for_preferred_partner_status({"V1": 95.0, "V2": 80.0}, 90.0) == ["V1"]
