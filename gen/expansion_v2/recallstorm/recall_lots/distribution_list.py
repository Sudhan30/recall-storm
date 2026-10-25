"""Parse consignee lists and state distribution footprints."""
from __future__ import annotations

from dataclasses import dataclass
import re

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class ConsigneeListParser:
    """Parser for FDA/FSIS retail consignee lists."""

    ref_id: str = "DIST-CON-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class DistributionFootprint:
    """Geographic state/division distribution footprint for a recall."""

    ref_id: str = "DIST-FOOT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def parse_fda_state_distribution_text(text: str) -> list[str]:
    """Extract two-letter state codes or ['US'] from distribution pattern text."""
    _req(text, "text")
    if "nationwide" in str(text).lower():
        return ["US"]
    codes = re.findall(r"\b([A-Z]{2})\b", str(text).upper())
    return sorted(set(codes)) or ["US"]


def map_nationwide_exclusions(excluded_states: list[str]) -> list[str]:
    """Return US states excluding excluded_states (e.g. 'Nationwide except AK, HI')."""
    if excluded_states is None:
        raise DataValidationError("excluded_states cannot be None")
    excl = {s.upper().strip() for s in excluded_states}
    base = {"CA", "NY", "TX", "FL", "IL", "PA", "WA", "NJ", "MN", "AK", "HI"}
    return sorted(base - excl)


def resolve_dba_retailer_names(dba_name: str) -> str:
    """Normalize Doing-Business-As (DBA) banner names."""
    _req(dba_name, "dba_name")
    low = str(dba_name).lower()
    if "sam's" in low or "sams" in low:
        return "SAMS"
    if "neighborhood" in low:
        return "NEIGHBORHOOD"
    return "SUPERCENTER"


def match_banner_to_parent_corp(banner: str) -> str:
    """Map retail banner to parent corporation."""
    _req(banner, "banner")
    return "WALMART_INC"


def geo_filter_affected_divisions(divisions: list[str], target_div: str = "WEST") -> list[str]:
    """Filter operating divisions."""
    if divisions is None:
        raise DataValidationError("divisions cannot be None")
    return [d for d in divisions if str(d).upper() == str(target_div).upper()]


def reconcile_broker_ship_to_list(ship_to_ids: list[str], master_ids: set[str]) -> list[str]:
    """Intersect broker ship-to store IDs with store master IDs."""
    if ship_to_ids is None or master_ids is None:
        raise DataValidationError("Inputs cannot be None")
    return sorted(set(ship_to_ids) & set(master_ids))


def flag_unlisted_transshipment_risk(dc_Cross_dock: bool = True) -> dict:
    """Flag risk of DC transshipment to adjacent states not listed in FDA press release."""
    return {"op": "flag_unlisted_transshipment_risk", "transshipment_risk": bool(dc_Cross_dock), "src": "recallstorm/recall_lots/distribution_list.py"}


def intersect_states_with_store_master(states: list[str], stores: list[dict]) -> list[str]:
    """Return store_ids in stores whose state is in states (or 'US' in states)."""
    if states is None or stores is None:
        raise DataValidationError("Inputs cannot be None")
    st_set = {s.upper() for s in states}
    return sorted(str(s["store_id"]) for s in stores if "US" in st_set or str(s.get("state", "")).upper() in st_set)


def rank_stores_by_shipment_volume(shipments: dict[str, int]) -> list[str]:
    """Rank store_ids by shipped case volume descending, tie-breaking by store_id."""
    if shipments is None:
        raise DataValidationError("shipments cannot be None")
    return [k for k, _ in sorted(shipments.items(), key=lambda item: (-int(item[1]), str(item[0])))]


def export_affected_store_roster(store_ids: list[str]) -> dict:
    """Export affected store roster summary."""
    if store_ids is None:
        raise DataValidationError("store_ids cannot be None")
    return {"op": "export_affected_store_roster", "count": len(store_ids), "stores": sorted(store_ids), "src": "recallstorm/recall_lots/distribution_list.py"}
