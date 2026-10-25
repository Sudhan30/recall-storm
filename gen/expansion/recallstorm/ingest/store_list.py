"""Store CSV parser, geocoding helpers, district/DC assignment, and validation."""
from __future__ import annotations

import csv
import io
from contract import Store, StoreFormat
from recallstorm.core.errors import DataValidationError
from recallstorm.core.validate import validate_store

_ZIP_COORDS: dict[str, tuple[float, float]] = {
    "90631": (33.91287, -117.97008),
    "93551": (34.60838, -118.14441),
    "95993": (39.13926, -121.64549),
    "95678": (38.78642, -121.28773),
    "93309": (35.29875, -119.02938),
}


def normalize_store_format(fmt_str: str | StoreFormat) -> StoreFormat:
    """Normalize a store format string into a StoreFormat enum."""
    if isinstance(fmt_str, StoreFormat):
        return fmt_str
    if not isinstance(fmt_str, str) or not fmt_str.strip():
        raise DataValidationError("Store format must be a non-empty string")
    s = fmt_str.strip().upper()
    if "SAMS" in s or "CLUB" in s:
        return StoreFormat.SAMS
    if "NEIGHBORHOOD" in s or "NHM" in s:
        return StoreFormat.NEIGHBORHOOD
    if "DISCOUNT" in s:
        return StoreFormat.DISCOUNT
    if "SUPER" in s or "WM" in s:
        return StoreFormat.SUPERCENTER
    raise DataValidationError(f"Unrecognized store format: {fmt_str}")


def parse_address(addr: str) -> dict[str, str]:
    """Parse a single-line address into street, city, state, and zip_code."""
    if not isinstance(addr, str) or not addr.strip():
        raise DataValidationError("Address must be a non-empty string")
    parts = [p.strip() for p in addr.split(",")]
    street = parts[0]
    city = parts[1] if len(parts) > 1 else "Unknown"
    state_zip = parts[2].split() if len(parts) > 2 else ["CA", "90001"]
    state = state_zip[0] if state_zip else "CA"
    zip_code = state_zip[1] if len(state_zip) > 1 else "90001"
    return {"street": street, "city": city, "state": state.upper(), "zip": zip_code}


def geocode_zip(zip_code: str) -> tuple[float, float]:
    """Return deterministic (lat, lon) coordinates for a 5-digit ZIP code."""
    if not isinstance(zip_code, str) or not zip_code.strip():
        raise DataValidationError("zip_code must be non-empty")
    z = zip_code.strip()[:5]
    if z in _ZIP_COORDS:
        return _ZIP_COORDS[z]
    num = int("".join(c for c in z if c.isdigit()) or "90000")
    lat = round(33.0 + (num % 900) / 100.0, 5)
    lon = round(-117.0 - (num % 500) / 100.0, 5)
    return lat, lon


def assign_district(lat: float, lon: float, state: str = "CA") -> str:
    """Assign a regional district ID based on latitude."""
    if lat >= 37.5:
        return "D01"
    if lat >= 34.4:
        return "D06"
    return "D09"


def assign_dc(lat: float, lon: float, state: str = "CA") -> str:
    """Assign the nearest Distribution Center ID based on latitude."""
    if lat >= 37.5:
        return "DC_NORTH"
    if lat >= 34.4:
        return "DC_CENTRAL"
    return "DC_SOUTH"


def store_from_row(row: dict) -> Store:
    """Build a Store dataclass from a dictionary row."""
    if not isinstance(row, dict) or not row.get("store_id"):
        raise DataValidationError("Store row requires store_id")
    fmt = normalize_store_format(row.get("format", "SUPERCENTER"))
    state = str(row.get("state", "CA")).strip().upper()
    city = str(row.get("city", "Los Angeles")).strip()
    if "lat" in row and "lon" in row:
        lat, lon = float(row["lat"]), float(row["lon"])
    else:
        lat, lon = geocode_zip(str(row.get("zip", "90631")))
    district = str(row.get("district") or assign_district(lat, lon, state)).strip()
    dc_id = str(row.get("dc_id") or assign_dc(lat, lon, state)).strip()
    tz = str(row.get("tz", "America/Los_Angeles")).strip()
    return Store(
        store_id=str(row["store_id"]).strip(),
        format=fmt,
        state=state,
        city=city,
        lat=lat,
        lon=lon,
        district=district,
        dc_id=dc_id,
        tz=tz,
    )


def parse_store_csv(text: str) -> list[dict]:
    """Parse CSV text of stores into a list of row dicts."""
    if not isinstance(text, str) or not text.strip():
        raise DataValidationError("CSV text is empty")
    reader = csv.DictReader(io.StringIO(text.strip()))
    return [dict(r) for r in reader]


def dedupe_stores(stores: list[Store]) -> list[Store]:
    """Deduplicate stores by store_id, preserving order."""
    seen: set[str] = set()
    out: list[Store] = []
    for s in stores:
        if s.store_id not in seen:
            seen.add(s.store_id)
            out.append(s)
    return out


def validate_store_list(stores: list[Store]) -> list[str]:
    """Validate a list of Store objects."""
    issues: list[str] = []
    for s in stores:
        issues.extend(validate_store(s))
    return issues
