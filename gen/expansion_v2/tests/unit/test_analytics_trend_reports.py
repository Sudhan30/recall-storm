"""Unit tests for recallstorm.analytics.trend_reports."""
from recallstorm.analytics.trend_reports import (
    HistoricalRecallTrends,
    LongitudinalComplianceView,
    analyze_additive_ban_readiness_burn_down,
    chart_allergen_vs_micro_recall_proportions,
    compare_q_over_q_time_to_100_pct_closure,
    correlate_staff_turnover_with_drill_scores,
    export_longitudinal_dataset_to_parquet,
    generate_annual_food_safety_review_charts,
    identify_chronic_bottleneck_store_formats,
    measure_year_over_year_shrink_recovery_pct,
    plot_monthly_recall_volume_by_fda_class,
    track_repeat_offender_vendor_trajectories,
)


def test_trend_reports():
    assert HistoricalRecallTrends().status == "ACTIVE"
    assert LongitudinalComplianceView().status == "ACTIVE"
    assert plot_monthly_recall_volume_by_fda_class({"Class I": 3, "Class II": 5})["total"] == 8
    assert analyze_additive_ban_readiness_burn_down([100, 60, 15])["net_reduction"] == 85
    assert track_repeat_offender_vendor_trajectories({"V1": 3, "V2": 1}, 2) == ["V1"]
    assert compare_q_over_q_time_to_100_pct_closure(140.0, 110.0)["improved"] is True
    assert identify_chronic_bottleneck_store_formats({"SUPERCENTER": 120.0, "NEIGHBORHOOD": 70.0}) == "SUPERCENTER"
    assert correlate_staff_turnover_with_drill_scores(55.0, 75.0)["at_risk"] is True
    props = chart_allergen_vs_micro_recall_proportions(5, 3, 2)
    assert props["allergen"] == 0.5
    assert measure_year_over_year_shrink_recovery_pct(9000.0, 10000.0) == 90.0
    assert generate_annual_food_safety_review_charts(2026, 12)["total_drills"] == 12
    assert export_longitudinal_dataset_to_parquet("trends.parquet", 50)["row_count"] == 50
