"""Unit tests for recallstorm.recall_lots.distribution_list."""
from recallstorm.recall_lots.distribution_list import (
    ConsigneeListParser,
    DistributionFootprint,
    export_affected_store_roster,
    flag_unlisted_transshipment_risk,
    geo_filter_affected_divisions,
    intersect_states_with_store_master,
    map_nationwide_exclusions,
    match_banner_to_parent_corp,
    parse_fda_state_distribution_text,
    rank_stores_by_shipment_volume,
    reconcile_broker_ship_to_list,
    resolve_dba_retailer_names,
)


def test_distribution_list():
    assert ConsigneeListParser().status == "ACTIVE"
    assert DistributionFootprint().status == "ACTIVE"
    assert parse_fda_state_distribution_text("Distributed in CA, NV, OR") == ["CA", "NV", "OR"]
    assert "AK" not in map_nationwide_exclusions(["AK", "HI"])
    assert resolve_dba_retailer_names("Sam's Club") == "SAMS"
    assert match_banner_to_parent_corp("Walmart") == "WALMART_INC"
    assert geo_filter_affected_divisions(["WEST", "EAST"], "WEST") == ["WEST"]
    assert reconcile_broker_ship_to_list(["WM1", "WM2"], {"WM1"}) == ["WM1"]
    assert flag_unlisted_transshipment_risk(True)["transshipment_risk"] is True
    assert intersect_states_with_store_master(["CA"], [{"store_id": "WM1", "state": "CA"}]) == ["WM1"]
    assert rank_stores_by_shipment_volume({"WM1": 10, "WM2": 25}) == ["WM2", "WM1"]
    assert export_affected_store_roster(["WM1"])["count"] == 1
