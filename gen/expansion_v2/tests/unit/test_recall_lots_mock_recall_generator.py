"""Unit tests for recallstorm.recall_lots.mock_recall_generator."""
from recallstorm.recall_lots.mock_recall_generator import (
    MockLotInjector,
    SyntheticRecallScenario,
    build_expected_ground_truth_key,
    configure_blind_drill_parameters,
    create_multi_dc_split_scenario,
    generate_mock_press_release_pdf,
    generate_realistic_lot_typos,
    inject_seeded_lots_into_wms,
    plant_decoy_unaffected_lots,
    scale_scenario_store_count,
    synthesize_class_i_listeria_notice,
    validate_scenario_solvability,
)


def test_mock_recall_generator():
    assert SyntheticRecallScenario().status == "ACTIVE"
    assert MockLotInjector().status == "ACTIVE"
    assert synthesize_class_i_listeria_notice("S1", "L1")["class"] == "Class I"
    assert inject_seeded_lots_into_wms("DC1", ["L1", "L2"])["count"] == 2
    assert len(generate_realistic_lot_typos("L2601")) == 3
    assert create_multi_dc_split_scenario(["DC1", "DC2"], 10)["total_cases"] == 20
    assert configure_blind_drill_parameters("DR1", 4)["duration_hours"] == 4
    assert len(plant_decoy_unaffected_lots("L2601")) == 2
    assert len(scale_scenario_store_count(["WM1", "WM2"], 3)) == 6
    assert generate_mock_press_release_pdf("DR1")["watermark"] == "EXERCISE ONLY"
    assert build_expected_ground_truth_key(["S1"], ["S2"])["PULL"] == ["S1"]
    assert validate_scenario_solvability(120.0, 240.0)["solvable"] is True
