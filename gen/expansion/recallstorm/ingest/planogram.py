"""Planogram parser, location codes, bay capacities, and planogram diffing."""
from __future__ import annotations

import re
from contract import Facing, Location, StoreFormat
from recallstorm.core.errors import DataValidationError
from recallstorm.core.validate import validate_facing

_LOC_CODE_RE = re.compile(r"^([A-Z]\d{2})-B(\d+)-S(\d+)-P(\d+)$", re.IGNORECASE)


def location_from_code(code: str) -> Location:
    """Parse a compact location code like 'A01-B1-S4-P3' into a Location."""
    if not isinstance(code, str) or not code.strip():
        raise DataValidationError("Location code must be a non-empty string")
    m = _LOC_CODE_RE.match(code.strip())
    if not m:
        raise DataValidationError(f"Invalid location code format: {code}")
    return Location(aisle=m.group(1).upper(), bay=int(m.group(2)), shelf=int(m.group(3)), pos=int(m.group(4)))


def parse_planogram_row(row: dict) -> dict:
    """Parse and validate a single planogram row dictionary."""
    if not isinstance(row, dict) or not row.get("store_id") or not row.get("sku_id"):
        raise DataValidationError("Planogram row requires store_id and sku_id")
    if isinstance(row.get("loc"), dict):
        loc_d = row["loc"]
        loc = Location(str(loc_d["aisle"]), int(loc_d["bay"]), int(loc_d["shelf"]), int(loc_d["pos"]))
    elif isinstance(row.get("loc"), Location):
        loc = row["loc"]
    elif isinstance(row.get("loc_code"), str):
        loc = location_from_code(row["loc_code"])
    else:
        raise DataValidationError("Planogram row requires loc or loc_code")
    return {
        "store_id": str(row["store_id"]).strip(),
        "sku_id": str(row["sku_id"]).strip(),
        "loc": loc,
        "units": int(row.get("units", 12)),
    }


def planogram_to_facings(rows: list[dict]) -> list[Facing]:
    """Convert a list of planogram row dicts into Facing dataclasses."""
    return [Facing(**parse_planogram_row(r)) for r in rows]


def bay_capacity(loc: Location) -> int:
    """Return estimated max unit capacity for a shelf location."""
    if not isinstance(loc, Location):
        raise TypeError("loc must be a Location")
    return 48 if loc.shelf == 1 else 36


def shelf_positions(aisle: str, bay: int, shelves: int = 5, pos_per_shelf: int = 6) -> list[Location]:
    """Enumerate all Location slots in a bay."""
    if bay <= 0 or shelves <= 0 or pos_per_shelf <= 0:
        raise ValueError("bay, shelves, and pos_per_shelf must be positive")
    out: list[Location] = []
    for s in range(1, shelves + 1):
        for p in range(1, pos_per_shelf + 1):
            out.append(Location(aisle=aisle, bay=bay, shelf=s, pos=p))
    return out


def merge_planograms(*facing_lists: list[Facing]) -> list[Facing]:
    """Merge multiple lists of Facings, summing units at identical (store_id, sku_id, loc)."""
    merged: dict[tuple[str, str, Location], int] = {}
    for flist in facing_lists:
        for f in flist:
            key = (f.store_id, f.sku_id, f.loc)
            merged[key] = merged.get(key, 0) + f.units
    return [
        Facing(store_id=st, sku_id=sk, loc=loc, units=u)
        for (st, sk, loc), u in sorted(merged.items(), key=lambda x: (x[0][0], x[0][2].aisle, x[0][2].bay, x[0][1]))
    ]


def planogram_diff(old_facings: list[Facing], new_facings: list[Facing]) -> dict[str, list[Facing]]:
    """Compute added and removed facings between two planograms."""
    old_map = {(f.store_id, f.sku_id, f.loc): f for f in old_facings}
    new_map = {(f.store_id, f.sku_id, f.loc): f for f in new_facings}
    added = [f for k, f in new_map.items() if k not in old_map]
    removed = [f for k, f in old_map.items() if k not in new_map]
    return {"added": added, "removed": removed}


def facing_units_estimate(fmt: StoreFormat | str, category: str = "candy") -> int:
    """Estimate default shelf units based on store format and product category."""
    f = fmt.value if isinstance(fmt, StoreFormat) else str(fmt).upper()
    base = 24 if f == "SAMS" else (18 if f == "SUPERCENTER" else 12)
    return base + 6 if "candy" in category.lower() else base


def validate_planogram(facings: list[Facing]) -> list[str]:
    """Validate a list of Facing objects."""
    issues: list[str] = []
    for f in facings:
        issues.extend(validate_facing(f))
    return issues
