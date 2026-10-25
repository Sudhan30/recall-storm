"""StoreFormat profiles, category carrying rules, and priorities."""
from __future__ import annotations

from contract import Store, StoreFormat

_PROFILES: dict[StoreFormat, dict] = {
    StoreFormat.SUPERCENTER: {
        "labor_minutes": 480.0,
        "tag_rule": "ESL_AND_PAPER",
        "backroom_capacity": 600,
        "priority": 1,
    },
    StoreFormat.SAMS: {
        "labor_minutes": 420.0,
        "tag_rule": "PALLET_SIGN",
        "backroom_capacity": 900,
        "priority": 2,
    },
    StoreFormat.DISCOUNT: {
        "labor_minutes": 360.0,
        "tag_rule": "PAPER_TAG",
        "backroom_capacity": 350,
        "priority": 3,
    },
    StoreFormat.NEIGHBORHOOD: {
        "labor_minutes": 300.0,
        "tag_rule": "ESL_ONLY",
        "backroom_capacity": 250,
        "priority": 4,
    },
}


def format_profile(fmt: StoreFormat) -> dict:
    """Return the operational profile dictionary for a StoreFormat."""
    if not isinstance(fmt, StoreFormat):
        fmt = StoreFormat(str(fmt).upper())
    return dict(_PROFILES[fmt])


def is_club_format(fmt: StoreFormat) -> bool:
    """Return True if fmt is StoreFormat.SAMS."""
    return fmt == StoreFormat.SAMS


def carries_category(fmt: StoreFormat, category: str) -> bool:
    """Return True if a store format carries the given product category."""
    cat = (category or "").lower()
    if fmt == StoreFormat.NEIGHBORHOOD and "automotive" in cat:
        return False
    return True


def format_labor_minutes(fmt: StoreFormat) -> float:
    """Return baseline recall labor budget in minutes for fmt."""
    return float(format_profile(fmt)["labor_minutes"])


def format_tag_rule(fmt: StoreFormat) -> str:
    """Return the shelf tagging protocol for fmt."""
    return str(format_profile(fmt)["tag_rule"])


def format_backroom_capacity(fmt: StoreFormat) -> int:
    """Return backroom case staging capacity for fmt."""
    return int(format_profile(fmt)["backroom_capacity"])


def format_priority(fmt: StoreFormat) -> int:
    """Return priority rank (1 = highest) for fmt."""
    return int(format_profile(fmt)["priority"])


def formats_in_pack(stores: list[Store]) -> list[StoreFormat]:
    """Return distinct StoreFormats present in stores sorted by priority."""
    present = {s.format for s in stores}
    return sorted(present, key=format_priority)


def format_summary(stores: list[Store]) -> dict[str, int]:
    """Return counts of stores per StoreFormat value."""
    counts = {f.value: 0 for f in StoreFormat}
    for s in stores:
        counts[s.format.value] = counts.get(s.format.value, 0) + 1
    return counts
