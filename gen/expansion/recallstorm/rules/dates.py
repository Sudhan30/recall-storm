"""Effective date comparisons and timezone-aware store deadline calculations."""
from __future__ import annotations

from datetime import datetime
from contract import Rule, Store
from recallstorm.core.clock import from_local, local_wall


def effective_at(rule: Rule, at: datetime, tz_name: str | None = None) -> bool:
    """Return True if rule is in effect at instant `at` (local(at) >= rule.effective)."""
    if not isinstance(rule, Rule):
        raise TypeError("rule must be a Rule")
    if not isinstance(at, datetime):
        raise TypeError("at must be a datetime")
    wall = local_wall(at, tz_name)
    rule_eff = rule.effective.replace(tzinfo=None)
    return wall >= rule_eff


def is_prohibited_at(rule: Rule, at: datetime, tz_name: str | None = None) -> bool:
    """Alias for effective_at: sale is prohibited when local(at) >= rule.effective."""
    return effective_at(rule, at, tz_name)


def sell_through_allowed(rule: Rule, at: datetime, tz_name: str | None = None) -> bool:
    """Return True if sale is still permitted at `at` (local(at) < rule.effective)."""
    return not effective_at(rule, at, tz_name)


def days_until_effective(rule: Rule, at: datetime, tz_name: str | None = None) -> int:
    """Return whole days remaining from `at` until `rule.effective` in local time."""
    wall = local_wall(at, tz_name)
    rule_eff = rule.effective.replace(tzinfo=None)
    return (rule_eff.date() - wall.date()).days


def first_prohibited_instant(rule: Rule, tz_name: str = "America/Los_Angeles") -> datetime:
    """Return the tz-aware instant at which sale becomes prohibited in tz_name."""
    if not isinstance(rule, Rule):
        raise TypeError("rule must be a Rule")
    return from_local(rule.effective.replace(tzinfo=None), tz_name)


def local_deadline(rule: Rule, tz_name: str = "America/Los_Angeles") -> datetime:
    """Return the tz-aware deadline for pulling inventory before rule.effective."""
    return first_prohibited_instant(rule, tz_name)


def deadline_for_store(rule: Rule, store: Store) -> datetime:
    """Return the tz-aware deadline for a specific Store in its Store.tz."""
    if not isinstance(store, Store):
        raise TypeError("store must be a Store")
    return first_prohibited_instant(rule, store.tz)


def deadlines_by_tz(rule: Rule, tz_names: list[str] | tuple[str, ...]) -> dict[str, datetime]:
    """Map each timezone name to the tz-aware effective instant of rule."""
    return {tz: first_prohibited_instant(rule, tz) for tz in tz_names}


def next_effective_rule(
    rules: list[Rule],
    at: datetime,
    tz_name: str | None = None,
) -> Rule | None:
    """Return the earliest rule whose effective date is >= local(at)."""
    wall = local_wall(at, tz_name)
    upcoming = [r for r in rules if r.effective.replace(tzinfo=None) >= wall]
    if not upcoming:
        return None
    return min(upcoming, key=lambda r: (r.effective.replace(tzinfo=None), r.rule_id))
