"""Unit tests for recallstorm.ingest.store_list."""
from contract import StoreFormat
from recallstorm.ingest.store_list import (
    assign_dc,
    assign_district,
    dedupe_stores,
    geocode_zip,
    normalize_store_format,
    parse_address,
    parse_store_csv,
    store_from_row,
    validate_store_list,
)


def test_store_list_parsing():
    csv_data = "store_id,format,state,city,lat,lon\nWM1563,SUPERCENTER,CA,Lancaster,34.6938,-118.17406\n"
    stores = parse_store_csv(csv_data)
    assert len(stores) == 1
    assert stores[0].dc_id == "DC_CENTRAL"
    assert stores[0].district == "D06"
    assert normalize_store_format("Sam's Club") == StoreFormat.SAMS
    assert normalize_store_format("Neighborhood Market") == StoreFormat.NEIGHBORHOOD
    assert assign_dc(39.0, -121.0) == "DC_NORTH"
    assert assign_district(33.9, -117.9) == "D09"
    assert parse_address("100 Main St, Corona, CA")["city"] == "Corona"
    lat, lon = geocode_zip("90210")
    assert 30.0 <= lat <= 45.0 and -125.0 <= lon <= -110.0
    st2 = store_from_row({"store_id": "SAMS1", "format": "SAMS", "lat": 33.9, "lon": -117.9})
    assert len(dedupe_stores([stores[0], stores[0], st2])) == 2
    assert validate_store_list(stores) == []
