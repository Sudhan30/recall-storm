"""Unit tests for recallstorm.analytics.risk_scoring."""
from recallstorm.analytics.risk_scoring import (
    CategoryExposureModel,
    StoreRiskProfile,
    assess_high_shrink_store_phantom_stock_risk,
    calculate_demographic_vulnerable_pop_index,
    combine_factors_into_composite_risk_tier,
    model_regulatory_fine_multiplier_by_state,
    predict_understaffed_shift_execution_lag,
    prioritize_high_risk_stores_for_floaters,
    rank_suppliers_by_import_detention_history,
    score_store_by_historical_audit_failures,
    update_risk_weights_from_post_mortem,
    weight_category_by_fda_recall_frequency,
)


def test_risk_scoring():
    assert StoreRiskProfile().status == "ACTIVE"
    assert CategoryExposureModel().status == "ACTIVE"
    assert score_store_by_historical_audit_failures(2, 10) == 0.2
    assert weight_category_by_fda_recall_frequency("baking decorations") == 3.5
    assert calculate_demographic_vulnerable_pop_index(10.0, 20.0) == 0.5
    assert assess_high_shrink_store_phantom_stock_risk(4.5, 3.0)["high_phantom_risk"] is True
    assert rank_suppliers_by_import_detention_history({"V1": 1, "V2": 5}) == ["V2", "V1"]
    assert model_regulatory_fine_multiplier_by_state("CA") == 2.5
    assert predict_understaffed_shift_execution_lag(300.0, 200.0) == 100.0
    assert combine_factors_into_composite_risk_tier(85.0) == "CRITICAL"
    assert prioritize_high_risk_stores_for_floaters({"WM1": 40.0, "WM2": 90.0}) == ["WM2", "WM1"]
    assert update_risk_weights_from_post_mortem(1.0, True) == 1.2
