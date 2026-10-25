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


def test_store_list_pipeline():
    csv_text = "store_id,format,state,city,lat,lon\nWM1563,SUPERCENTER,CA,Lancaster,34.6938,-118.17406\n"
    rows = parse_store_csv(csv_text)
    assert len(rows) == 1
    st = store_from_row(rows[0])
    assert st.format == StoreFormat.SUPERCENTER
    assert st.district == "D06"
    assert st.dc_id == "DC_CENTRAL"
    assert validate_store_list([st]) == []
    assert len(dedupe_stores([st, st])) == 1
    assert normalize_store_format("Sam's Club") == StoreFormat.SAMS
    addr = parse_address("1400 South Beach Blvd, La Habra, CA 90631")
    assert addr["city"] == "La Habra"
    lat, lon = geocode_zip("90631")
    assert assign_district(lat, lon) == "D09"
    assert assign_dc(lat, lon) == "DC_SOUTH"
