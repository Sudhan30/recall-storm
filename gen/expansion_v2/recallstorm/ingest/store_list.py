"""Parse store CSVs, normalize formats, and assign districts/DCs."""
from __future__ import annotations

import csv
import io

from contract import Store, StoreFormat
from recallstorm.core.errors import DataValidationError
from recallstorm.core.validate import validate_store


def normalize_store_format(raw_fmt: str) -> StoreFormat:
    """Normalize a raw store format string to a StoreFormat enum."""
    s = (raw_fmt or "").upper().strip()
    if "SAM" in s or "CLUB" in s:
        return StoreFormat.SAMS
    if "NEIGHBOR" in s or "MARKET" in s:
        return StoreFormat.NEIGHBORHOOD
    if "DISCOUNT" in s:
        return StoreFormat.DISCOUNT
    if "SUPER" in s or s == "WM":
        return StoreFormat.SUPERCENTER
    try:
        return StoreFormat(s)
    except ValueError as exc:
        raise DataValidationError(f"Unrecognized store format: {raw_fmt!r}") from exc


def parse_address(addr: str) -> dict:
    """Parse a street address string into street, city, state, zip_code."""
    parts = [p.strip() for p in (addr or "").split(",")]
    return {
        "street": parts[0] if parts else "",
        "city": parts[1] if len(parts) > 1 else "Unknown",
        "state": parts[2][:2].upper() if len(parts) > 2 else "CA",
    }


def geocode_zip(zip_code: str) -> tuple[float, float]:
    """Deterministic coordinate lookup from a 5-digit US ZIP code."""
    digits = "".join(c for c in str(zip_code) if c.isdigit())
    if not digits:
        return (34.0522, -118.2437)
    n = int(digits[:5])
    lat = 32.5 + (n % 1000) * 0.008
    lon = -122.5 + (n % 500) * 0.01
    return (round(lat, 5), round(lon, 5))


def assign_district(lat: float, lon: float, state: str = "CA") -> str:
    """Assign a store district code based on latitude."""
    if lat >= 37.5:
        return "D01"
    if lat >= 34.4:
        return "D06"
    return "D09"


def assign_dc(lat: float, lon: float, state: str = "CA") -> str:
    """Assign a regional distribution center ID based on latitude."""
    if lat >= 37.5:
        return "DC_NORTH"
    if lat >= 34.4:
        return "DC_CENTRAL"
    return "DC_SOUTH"


def store_from_row(row: dict) -> Store:
    """Build a Store dataclass from a dictionary row."""
    if not isinstance(row, dict) or not row.get("store_id"):
        raise DataValidationError("Store row requires store_id")
    lat = float(row.get("lat", 34.05))
    lon = float(row.get("lon", -118.24))
    state = str(row.get("state", "CA")).strip().upper()
    return Store(
        store_id=str(row["store_id"]).strip(),
        format=normalize_store_format(str(row.get("format", "SUPERCENTER"))),
        state=state,
        city=str(row.get("city", "Los Angeles")).strip(),
        lat=lat,
        lon=lon,
        district=str(row.get("district") or assign_district(lat, lon, state)).strip(),
        dc_id=str(row.get("dc_id") or assign_dc(lat, lon, state)).strip(),
        tz=str(row.get("tz", "America/Los_Angeles")).strip(),
    )


def parse_store_csv(csv_text: str) -> list[Store]:
    """Parse CSV text into a list of Store objects."""
    if not isinstance(csv_text, str) or not csv_text.strip():
        return []
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    return [store_from_row(r) for r in reader]


def dedupe_stores(stores: list[Store]) -> list[Store]:
    """Deduplicate Store objects by store_id preserving order."""
    seen: set[str] = set()
    out: list[Store] = []
    for st in stores:
        if st.store_id not in seen:
            seen.add(st.store_id)
            out.append(st)
    return out


def validate_store_list(stores: list[Store]) -> list[str]:
    """Validate a list of Store objects."""
    issues: list[str] = []
    for st in stores:
        issues.extend(validate_store(st))
    return issues
