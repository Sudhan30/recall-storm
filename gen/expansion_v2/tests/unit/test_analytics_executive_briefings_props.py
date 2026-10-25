"""Property tests for recallstorm.analytics.executive_briefings."""
from recallstorm.analytics.executive_briefings import update_live_geojson_store_completion_map


def test_geojson_feature_count_matches_stores():
    stores = [{"store_id": f"WM{i}", "lat": 34.0 + i * 0.1, "lon": -118.0} for i in range(12)]
    geo = update_live_geojson_store_completion_map(stores)
    assert len(geo["features"]) == 12
