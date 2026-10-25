"""Parse planogram data into shelf facings and locations."""
from __future__ import annotations

from contract import Facing, Location, Sku, StoreFormat
from recallstorm.core.errors import DataValidationError
from recallstorm.core.validate import validate_facing


def location_from_code(code: str) -> Location:
    """Parse a hyphenated location code like 'A01-02-03-04' into a Location."""
    if not isinstance(code, str) or "-" not in code:
        raise DataValidationError(f"Invalid location code: {code!r}")
    parts = [p.strip() for p in code.split("-")]
    if len(parts) != 4:
        raise DataValidationError(f"Location code requires 4 parts (aisle-bay-shelf-pos): {code!r}")
    return Location(aisle=parts[0], bay=int(parts[1]), shelf=int(parts[2]), pos=int(parts[3]))


def parse_planogram_row(row: dict) -> Facing:
    """Parse a dictionary row into a contract Facing."""
    if not isinstance(row, dict) or not row.get("store_id") or not row.get("sku_id"):
        raise DataValidationError("Planogram row requires store_id and sku_id")
    if isinstance(row.get("loc"), Location):
        loc = row["loc"]
    elif isinstance(row.get("loc"), dict):
        l_d = row["loc"]
        loc = Location(str(l_d["aisle"]), int(l_d["bay"]), int(l_d["shelf"]), int(l_d["pos"]))
    elif row.get("loc_code"):
        loc = location_from_code(str(row["loc_code"]))
    else:
        loc = Location(
            str(row.get("aisle", "A01")),
            int(row.get("bay", 1)),
            int(row.get("shelf", 1)),
            int(row.get("pos", 1)),
        )
    return Facing(
        store_id=str(row["store_id"]).strip(),
        sku_id=str(row["sku_id"]).strip(),
        loc=loc,
        units=int(row.get("units", 10)),
    )


def planogram_to_facings(rows: list[dict]) -> list[Facing]:
    """Convert a list of planogram dictionaries into Facing objects."""
    return [parse_planogram_row(r) for r in rows]


def bay_capacity(bay: int, shelf: int = 1) -> int:
    """Return standard unit capacity for a given bay and shelf."""
    if bay <= 0 or shelf <= 0:
        raise ValueError("bay and shelf must be positive")
    return 48


def shelf_positions(facings: list[Facing], aisle: str, bay: int) -> list[Location]:
    """Return sorted Locations for a specific aisle and bay."""
    locs = [f.loc for f in facings if f.loc.aisle == aisle and f.loc.bay == bay]
    return sorted(locs, key=lambda l: (l.shelf, l.pos))


def merge_planograms(*lists: list[Facing]) -> list[Facing]:
    """Merge multiple facing lists summing units at identical (store_id, sku_id, loc)."""
    merged: dict[tuple, Facing] = {}
    for flist in lists:
        for f in flist:
            key = (f.store_id, f.sku_id, f.loc)
            if key in merged:
                prev = merged[key]
                merged[key] = Facing(f.store_id, f.sku_id, f.loc, prev.units + f.units)
            else:
                merged[key] = f
    return list(merged.values())


def planogram_diff(old: list[Facing], new: list[Facing]) -> dict:
    """Compute added and removed (store_id, sku_id, loc) keys between two planograms."""
    old_keys = {(f.store_id, f.sku_id, f.loc) for f in old}
    new_keys = {(f.store_id, f.sku_id, f.loc) for f in new}
    return {"added": len(new_keys - old_keys), "removed": len(old_keys - new_keys)}


def facing_units_estimate(sku: Sku, fmt: StoreFormat) -> int:
    """Estimate default shelf units based on case_units and StoreFormat."""
    mult = 3 if fmt == StoreFormat.SAMS else (2 if fmt == StoreFormat.SUPERCENTER else 1)
    return max(1, sku.case_units * mult)


def validate_planogram(facings: list[Facing]) -> list[str]:
    """Validate a list of Facing objects."""
    issues: list[str] = []
    for f in facings:
        issues.extend(validate_facing(f))
    return issues
