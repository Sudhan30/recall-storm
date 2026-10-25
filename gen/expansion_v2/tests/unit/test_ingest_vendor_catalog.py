"""Unit tests for recallstorm.ingest.vendor_catalog."""
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


def test_vendor_catalog():
    row = {
        "sku_id": "V1",
        "gtin": "73621007017",
        "name": "Soda",
        "brand": "Fizz",
        "category": "Beverages",
        "ingredients": "WATER, SUGAR, BVO",
        "dsd": True,
        "case_units": 24,
        "case_cube_ft3": 1.8,
        "case_weight_lb": 20.0,
        "reformulation_date": "2026-11-01",
        "substitutes": "V2, V3",
        "contact_email": "recall@fizz.example",
    }
    parsed = parse_vendor_row(row)
    assert parsed["dsd"] is True
    assert vendor_dsd_flag(row) is True
    assert vendor_case_pack(row) == (24, 1.8, 20.0)
    assert vendor_reformulation_date(row) == "2026-11-01"
    assert vendor_sub_suggestions(row) == ["V2", "V3"]
    assert vendor_contacts(row)["email"] == "recall@fizz.example"
    sku = vendor_to_sku(row)
    assert len(sku.gtin) == 14
    cat = merge_vendor_catalog([row])
    assert isinstance(cat, VendorCatalog)
    assert "V1" in cat.skus
