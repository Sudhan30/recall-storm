"""Operational profiles and priorities for StoreFormat (SUPERCENTER, DISCOUNT, NEIGHBORHOOD, SAMS)."""
from __future__ import annotations

from contract import Action, Store, StoreFormat

_PROFILES: dict[StoreFormat, dict] = {
    StoreFormat.SUPERCENTER: {
        "priority": 1,
        "backroom_cases": 300,
        "tag_rule": "SHELF_CHANNEL_FLASH",
        "pull_mins": 3.0,
    },
    StoreFormat.SAMS: {
        "priority": 2,
        "backroom_cases": 500,
        "tag_rule": "PALLET_PLACARD",
        "pull_mins": 4.0,
    },
    StoreFormat.NEIGHBORHOOD: {
        "priority": 3,
        "backroom_cases": 150,
        "tag_rule": "SHELF_CHANNEL_FLASH",
        "pull_mins": 2.5,
    },
    StoreFormat.DISCOUNT: {
        "priority": 4,
        "backroom_cases": 150,
        "tag_rule": "SHELF_CHANNEL_FLASH",
        "pull_mins": 2.5,
    },
}


def _to_fmt(fmt: StoreFormat | str) -> StoreFormat:
    return fmt if isinstance(fmt, StoreFormat) else StoreFormat(str(fmt).strip().upper())


def format_profile(fmt: StoreFormat | str) -> dict:
    """Return the operational profile dictionary for a StoreFormat."""
    f = _to_fmt(fmt)
    return dict(_PROFILES[f])


def is_club_format(fmt: StoreFormat | str) -> bool:
    """Return True if the store format is SAMS club."""
    return _to_fmt(fmt) == StoreFormat.SAMS


def format_priority(fmt: StoreFormat | str) -> int:
    """Return numeric priority rank (1=highest) for a StoreFormat."""
    return int(_PROFILES[_to_fmt(fmt)]["priority"])


def format_backroom_capacity(fmt: StoreFormat | str) -> int:
    """Return backroom case staging capacity for a StoreFormat."""
    return int(_PROFILES[_to_fmt(fmt)]["backroom_cases"])


def format_tag_rule(fmt: StoreFormat | str) -> str:
    """Return signage rule name for a StoreFormat."""
    return str(_PROFILES[_to_fmt(fmt)]["tag_rule"])


def format_labor_minutes(fmt: StoreFormat | str, action: Action | str = Action.PULL) -> float:
    """Return baseline labor minutes per task for a StoreFormat and Action."""
    base = float(_PROFILES[_to_fmt(fmt)]["pull_mins"])
    act = action.value if isinstance(action, Action) else str(action).upper()
    if act == Action.TAG_FLASH.value:
        return 1.0
    if act == Action.PLACE_SUB.value:
        return base + 1.0
    return base


def carries_category(fmt: StoreFormat | str, category: str) -> bool:
    """Return True if the store format carries the given product category."""
    _to_fmt(fmt)
    return bool(category and category.strip())


def formats_in_pack(stores: list[Store]) -> list[StoreFormat]:
    """Return sorted unique StoreFormats present in a store list."""
    present = {s.format for s in stores}
    return sorted(present, key=lambda f: f.value)


def format_summary(stores: list[Store]) -> dict[str, int]:
    """Count stores per StoreFormat."""
    counts: dict[str, int] = {}
    for s in stores:
        k = s.format.value
        counts[k] = counts.get(k, 0) + 1
    return counts
