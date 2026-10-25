"""Vendor catalog parser: DSD flags, case packs, reformulation dates, and substitute suggestions."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from contract import Sku
from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class VendorCatalog:
    """Parsed vendor catalog wrapper."""

    rows: tuple[dict, ...]


def parse_vendor_row(row: dict) -> dict:
    """Validate and normalize a vendor catalog row."""
    if not isinstance(row, dict) or not row.get("sku_id") or not row.get("gtin"):
        raise DataValidationError("Vendor row requires sku_id and gtin")
    return {
        "sku_id": str(row["sku_id"]).strip(),
        "gtin": str(row["gtin"]).strip().zfill(14),
        "name": str(row.get("name", "Unknown")).strip(),
        "brand": str(row.get("brand", "Generic")).strip(),
        "category": str(row.get("category", "general")).strip().lower(),
        "ingredients": str(row.get("ingredients", "")).strip(),
        "is_food": bool(row.get("is_food", True)),
        "is_ingested_drug": bool(row.get("is_ingested_drug", False)),
        "case_units": int(row.get("case_units", 12)),
        "case_cube_ft3": float(row.get("case_cube_ft3", 1.5)),
        "case_weight_lb": float(row.get("case_weight_lb", 10.0)),
        "is_dsd": bool(row.get("is_dsd", False)),
        "reformulation_date": row.get("reformulation_date"),
        "substitutes": list(row.get("substitutes", [])),
        "vendor_contact": str(row.get("vendor_contact", "")).strip(),
    }


def vendor_case_pack(row: dict) -> tuple[int, float, float]:
    """Extract (case_units, case_cube_ft3, case_weight_lb) from a vendor row."""
    parsed = parse_vendor_row(row)
    return parsed["case_units"], parsed["case_cube_ft3"], parsed["case_weight_lb"]


def vendor_to_sku(row: dict) -> Sku:
    """Convert a vendor row dictionary to a contract Sku."""
    p = parse_vendor_row(row)
    return Sku(
        sku_id=p["sku_id"],
        gtin=p["gtin"],
        name=p["name"],
        brand=p["brand"],
        category=p["category"],
        ingredients=p["ingredients"],
        is_food=p["is_food"],
        is_ingested_drug=p["is_ingested_drug"],
        case_units=p["case_units"],
        case_cube_ft3=p["case_cube_ft3"],
        case_weight_lb=p["case_weight_lb"],
    )


def vendor_dsd_flag(row: dict) -> bool:
    """Return True if the vendor item is Direct Store Delivery (DSD)."""
    return bool(row.get("is_dsd", False))


def vendor_reformulation_date(row: dict) -> date | None:
    """Parse and return the vendor reformulation date if present."""
    val = row.get("reformulation_date")
    if not val:
        return None
    if isinstance(val, date):
        return val
    return date.fromisoformat(str(val)[:10])


def vendor_sub_suggestions(rows: list[dict]) -> dict[str, list[str]]:
    """Build a mapping from sku_id to suggested substitute sku_ids."""
    out: dict[str, list[str]] = {}
    for r in rows:
        p = parse_vendor_row(r)
        if p["substitutes"]:
            out[p["sku_id"]] = [str(s) for s in p["substitutes"]]
    return out


def merge_vendor_catalog(skus: list[Sku], vendor_rows: list[dict]) -> list[Sku]:
    """Merge vendor catalog rows into an existing SKU list, adding any missing SKUs."""
    by_id = {s.sku_id: s for s in skus}
    for r in vendor_rows:
        v_sku = vendor_to_sku(r)
        if v_sku.sku_id not in by_id:
            by_id[v_sku.sku_id] = v_sku
    return [by_id[k] for k in sorted(by_id)]


def vendor_contacts(rows: list[dict]) -> dict[str, str]:
    """Map brand names to vendor contact strings."""
    contacts: dict[str, str] = {}
    for r in rows:
        p = parse_vendor_row(r)
        if p["vendor_contact"]:
            contacts[p["brand"]] = p["vendor_contact"]
    return contacts
