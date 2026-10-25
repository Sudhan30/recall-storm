"""Unit tests for recallstorm.analytics.executive_briefings."""
from recallstorm.analytics.executive_briefings import (
    CSuiteDigestGenerator,
    CrisisWarRoomFeed,
    archive_war_room_decision_log_snapshots,
    compare_current_event_to_historical_baseline,
    format_mobile_friendly_ceo_flash_email,
    generate_general_counsel_privilege_summary,
    highlight_red_flag_non_compliant_districts,
    project_estimated_time_to_full_containment,
    summarize_media_and_regulator_touchpoints,
    synthesize_hourly_war_room_situation_report,
    track_class_i_hospitalization_escalations,
    update_live_geojson_store_completion_map,
)


def test_executive_briefings():
    assert CSuiteDigestGenerator().status == "ACTIVE"
    assert CrisisWarRoomFeed().status == "ACTIVE"
    assert synthesize_hourly_war_room_situation_report("R1", 95.0)["completion_pct"] == 95.0
    assert highlight_red_flag_non_compliant_districts({"D01": 95.0, "D06": 80.0}, 90.0) == ["D06"]
    assert project_estimated_time_to_full_containment(100, 50.0) == 2.0
    assert summarize_media_and_regulator_touchpoints(2, 5)["fda_calls"] == 2
    assert track_class_i_hospitalization_escalations(1)["ceo_alert"] is True
    assert compare_current_event_to_historical_baseline(120.0, 180.0)["faster_than_baseline"] is True
    assert "POS Locked: 100%" in format_mobile_friendly_ceo_flash_email("R1", "Red 3 Ban")
    assert "PRIVILEGED" in generate_general_counsel_privilege_summary("R1")["header"]
    geo = update_live_geojson_store_completion_map([{"store_id": "WM1", "lat": 34.0, "lon": -118.0}])
    assert geo["type"] == "FeatureCollection" and len(geo["features"]) == 1
    assert archive_war_room_decision_log_snapshots("R1", 3)["decisions_count"] == 3
