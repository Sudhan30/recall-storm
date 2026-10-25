"""Unit tests for recallstorm.food_safety.sampling_plans."""
from recallstorm.food_safety.sampling_plans import (
    IcmsfAcceptanceCriteria,
    MicrobiologicalSamplingPlan,
    archive_certificate_of_analysis,
    assign_composite_sub_sample_units,
    build_cpsc_destructive_test_lot,
    calculate_icmsf_case_class_plan,
    evaluate_wgs_snp_distance_match,
    flag_lab_turnaround_sla_breach,
    generate_aseptic_collection_protocol,
    manage_hold_and_test_release,
    parse_pcr_presumptive_positive,
    track_chain_of_custody_seal,
)


def test_sampling_plans():
    assert MicrobiologicalSamplingPlan().status == "ACTIVE"
    assert IcmsfAcceptanceCriteria().status == "ACTIVE"
    assert calculate_icmsf_case_class_plan(15) == {"case": 15, "n": 60, "c": 0}
    assert assign_composite_sub_sample_units(60, 15) == 4
    assert generate_aseptic_collection_protocol("S1", 375)["sample_g"] == 375
    assert track_chain_of_custody_seal("SEAL1", True)["valid"] is True
    assert parse_pcr_presumptive_positive("SMP1", 25.0)["presumptive_positive"] is True
    assert evaluate_wgs_snp_distance_match(4, 10)["clonal_match"] is True
    assert manage_hold_and_test_release("L1", 60, 60)["release_authorized"] is True
    assert flag_lab_turnaround_sla_breach(80.0, 72.0)["breached"] is True
    assert build_cpsc_destructive_test_lot("S1", 12)["units"] == 12
    assert archive_certificate_of_analysis("COA1", "L1")["coa_id"] == "COA1"
