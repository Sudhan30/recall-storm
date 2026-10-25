"""Store layout geometry, aisle ordering, and walking distances."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import re

from contract import Facing, Location, Store


@dataclass
class StoreLayout:
    """2D coordinate layout of a store's aisles and bays."""

    store_id: str
    locations: list[Location] = field(default_factory=list)


def _aisle_num(aisle: str) -> int:
    m = re.search(r"(\d+)", str(aisle))
    return int(m.group(1)) if m else 0


def bay_coordinates(aisle: str, bay: int) -> tuple[float, float]:
    """Compute (x_meters, y_meters) for an aisle and bay."""
    x = float(_aisle_num(aisle)) * 4.0
    y = float(max(0, bay)) * 2.5
    return (x, y)


def location_xy(loc: Location) -> tuple[float, float]:
    """Compute (x_meters, y_meters) for a Location."""
    return bay_coordinates(loc.aisle, loc.bay)


def walking_distance(loc1: Location, loc2: Location) -> float:
    """Compute Manhattan walking distance in meters between two store Locations."""
    x1, y1 = location_xy(loc1)
    x2, y2 = location_xy(loc2)
    return round(abs(x2 - x1) + abs(y2 - y1), 2)


def aisle_order(locations: list[Location]) -> list[Location]:
    """Order Locations in serpentine/lexicographic aisle->bay->shelf->pos order."""
    return sorted(locations, key=lambda l: (_aisle_num(l.aisle), l.aisle, l.bay, l.shelf, l.pos))


def nearest_location(origin: Location, candidates: list[Location]) -> Location | None:
    """Return the candidate Location with shortest walking distance from origin."""
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda c: (walking_distance(origin, c), c.aisle, c.bay, c.shelf, c.pos),
    )


def build_layout(store: Store, facings: list[Facing]) -> StoreLayout:
    """Build a StoreLayout for store from its shelf facings."""
    locs = aisle_order([f.loc for f in facings if f.store_id == store.store_id])
    return StoreLayout(store_id=store.store_id, locations=locs)


def layout_bounds(layout: StoreLayout) -> tuple[float, float]:
    """Return (max_x, max_y) dimensions in meters for layout."""
    if not layout.locations:
        return (0.0, 0.0)
    coords = [location_xy(l) for l in layout.locations]
    return (max(x for x, _ in coords), max(y for _, y in coords))


def layout_to_json(layout: StoreLayout) -> str:
    """Serialize a StoreLayout to a JSON string."""
    max_x, max_y = layout_bounds(layout)
    return json.dumps(
        {
            "store_id": layout.store_id,
            "location_count": len(layout.locations),
            "bounds": [max_x, max_y],
        },
        sort_keys=True,
    )
