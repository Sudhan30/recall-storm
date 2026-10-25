"""Store 2D floor layout, serpentine aisle ordering, and Manhattan walking distance."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from contract import Facing, Location, Store


@dataclass(frozen=True)
class StoreLayout:
    """2D coordinate layout of a store's aisles and bays."""

    store_id: str
    locations: tuple[Location, ...]


def _aisle_num(aisle: str) -> int:
    digits = "".join(c for c in aisle if c.isdigit())
    return int(digits) if digits else 0


def bay_coordinates(aisle: str, bay: int) -> tuple[float, float]:
    """Compute (x_ft, y_ft) floor coordinates for an (aisle, bay) pair."""
    if not isinstance(aisle, str) or not aisle.strip():
        raise ValueError("aisle must be a non-empty string")
    if bay < 0:
        raise ValueError("bay must be non-negative")
    a_idx = _aisle_num(aisle)
    return float(a_idx * 12), float(bay * 4)


def location_xy(loc: Location) -> tuple[float, float]:
    """Return (x_ft, y_ft) floor coordinates for a Location."""
    if not isinstance(loc, Location):
        raise TypeError("loc must be a Location")
    x, y = bay_coordinates(loc.aisle, loc.bay)
    return x, y + (loc.pos * 0.5)


def walking_distance(loc1: Location, loc2: Location) -> float:
    """Compute Manhattan walking distance in feet between two shelf Locations."""
    x1, y1 = location_xy(loc1)
    x2, y2 = location_xy(loc2)
    if x1 == x2:
        return round(abs(y2 - y1), 2)
    # Cross-aisle travel via front/rear action alley (y=0)
    return round(abs(x2 - x1) + y1 + y2, 2)


def aisle_order(locations: list[Location]) -> list[Location]:
    """Sort locations in serpentine aisle traversal order for efficient shelf picking."""
    def _key(loc: Location) -> tuple[int, str, int, int, int]:
        a_num = _aisle_num(loc.aisle)
        bay_dir = loc.bay if a_num % 2 == 1 else -loc.bay
        return (a_num, loc.aisle, bay_dir, loc.shelf, loc.pos)

    return sorted(locations, key=_key)


def nearest_location(origin: Location, candidates: list[Location]) -> Location:
    """Return the candidate Location with shortest walking distance from origin."""
    if not candidates:
        raise ValueError("candidates cannot be empty")
    return min(candidates, key=lambda c: (walking_distance(origin, c), c.aisle, c.bay, c.shelf, c.pos))


def build_layout(store: Store, facings: list[Facing]) -> StoreLayout:
    """Build a StoreLayout from a store's facings."""
    locs = aisle_order([f.loc for f in facings if f.store_id == store.store_id])
    return StoreLayout(store_id=store.store_id, locations=tuple(locs))


def layout_bounds(layout: StoreLayout) -> tuple[float, float, float, float]:
    """Return (min_x, min_y, max_x, max_y) bounding box of a StoreLayout."""
    if not layout.locations:
        return (0.0, 0.0, 0.0, 0.0)
    coords = [location_xy(loc) for loc in layout.locations]
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return min(xs), min(ys), max(xs), max(ys)


def layout_to_json(layout: StoreLayout) -> str:
    """Serialize a StoreLayout to JSON."""
    return json.dumps(
        {
            "store_id": layout.store_id,
            "locations": [
                {"aisle": l.aisle, "bay": l.bay, "shelf": l.shelf, "pos": l.pos}
                for l in layout.locations
            ],
        },
        sort_keys=True,
    )
