"""Effective date and local wall-clock prohibition checks."""
from __future__ import annotations

from datetime import datetime

from contract import Rule, Store
from recallstorm.core.clock import from_local, iso_with_offset, local_wall


def effective_at(rule: Rule, tz_name: str | None = None) -> datetime:
    """Return rule.effective as naive local wall-clock or attached to tz_name."""
    if tz_name:
        return from_local(rule.effective, tz_name)
    return rule.effective.replace(tzinfo=None)


def is_prohibited_at(rule: Rule, at: datetime, tz_name: str | None = None) -> bool:
    """Return True when local(at) >= rule.effective (sale prohibited at or after effective)."""
    wall = local_wall(at, tz_name=tz_name)
    return wall >= rule.effective.replace(tzinfo=None)


def sell_through_allowed(rule: Rule, at: datetime, tz_name: str | None = None) -> bool:
    """Return True when local(at) < rule.effective (product may still be sold)."""
    return not is_prohibited_at(rule, at, tz_name=tz_name)


def days_until_effective(rule: Rule, at: datetime, tz_name: str | None = None) -> float:
    """Return signed days remaining until rule.effective from local(at)."""
    wall = local_wall(at, tz_name=tz_name)
    eff = rule.effective.replace(tzinfo=None)
    return (eff - wall).total_seconds() / 86400.0


def first_prohibited_instant(rules: list[Rule]) -> datetime | None:
    """Return the earliest effective datetime across rules, or None."""
    if not rules:
        return None
    return min(r.effective for r in rules)


def local_deadline(rule: Rule, tz_name: str) -> datetime:
    """Return timezone-aware deadline for rule in tz_name."""
    return from_local(rule.effective, tz_name)


def deadline_for_store(rule: Rule, store: Store) -> datetime:
    """Return timezone-aware deadline for rule in store.tz."""
    return local_deadline(rule, store.tz)


def deadlines_by_tz(rule: Rule, tz_names: list[str]) -> dict[str, str]:
    """Return a dict mapping each timezone name to its ISO 8601 deadline with offset."""
    return {tz: iso_with_offset(local_deadline(rule, tz), tz) for tz in tz_names}


def next_effective_rule(rules: list[Rule], at: datetime) -> Rule | None:
    """Return the next rule taking effect at or after local(at), or None."""
    wall = local_wall(at)
    future = [r for r in rules if r.effective.replace(tzinfo=None) >= wall]
    if not future:
        return None
    return min(future, key=lambda r: (r.effective, r.rule_id))
