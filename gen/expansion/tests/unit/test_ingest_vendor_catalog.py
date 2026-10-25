"""Unit tests for recallstorm.ingest.vendor_catalog."""
from datetime import date
from recallstorm.ingest.vendor_catalog import (
    VendorCatalog,
    merge_vendor_catalog,
    parse_vendor_row,
    vendor_case_pack,
    vendor_contacts,
    vendor_dsd_flag,
    vendor_reformulation_date,
    vendor_sub_suggestions,
    vendor_to_sku,
)


def test_vendor_catalog_functions():
    row = {
        "sku_id": "V001",
        "gtin": "00012345678905",
        "name": "Chips",
        "brand": "Frito-Lay",
        "category": "Snacks",
        "ingredients": "POTATOES, SALT",
        "case_units": 24,
        "case_cube_ft3": 2.0,
        "case_weight_lb": 8.5,
        "is_dsd": True,
        "reformulation_date": "2026-11-01",
        "substitutes": ["V002"],
        "vendor_contact": "rep@fritolay.com",
    }
    parsed = parse_vendor_row(row)
    assert vendor_dsd_flag(parsed) is True
    assert vendor_case_pack(row) == (24, 2.0, 8.5)
    assert vendor_reformulation_date(row) == date(2026, 11, 1)
    sku = vendor_to_sku(row)
    assert sku.sku_id == "V001"
    assert vendor_sub_suggestions([row]) == {"V001": ["V002"]}
    assert vendor_contacts([row]) == {"Frito-Lay": "rep@fritolay.com"}
    merged = merge_vendor_catalog([], [row])
    assert len(merged) == 1
    cat = VendorCatalog((parsed,))
    assert len(cat.rows) == 1
