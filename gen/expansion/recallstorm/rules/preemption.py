"""State vs. federal rule preemption and conflict resolution."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from contract import Rule


@dataclass(frozen=True)
class PreemptionResolver:
    """Resolver for state and federal rules covering the same additive."""

    rules: tuple[Rule, ...]


def federal_rule_for(rules: list[Rule] | tuple[Rule, ...], additive: str) -> Rule | None:
    """Return the first federal ('US') rule for an additive."""
    add = additive.strip().upper()
    for r in rules:
        if r.additive.upper() == add and "US" in r.jurisdictions:
            return r
    return None


def state_rule_for(rules: list[Rule] | tuple[Rule, ...], additive: str, state: str) -> Rule | None:
    """Return the first state-specific rule for an additive and 2-letter state."""
    add = additive.strip().upper()
    st = state.strip().upper()
    for r in rules:
        if r.additive.upper() == add and st in r.jurisdictions:
            return r
    return None


def stricter_rule(r1: Rule, r2: Rule) -> Rule:
    """Return whichever rule has the earlier effective date (or wider scope on tie)."""
    if not isinstance(r1, Rule) or not isinstance(r2, Rule):
        raise TypeError("Both arguments must be Rule instances")
    if r1.effective != r2.effective:
        return r1 if r1.effective < r2.effective else r2
    return r1 if len(r1.applies_to) >= len(r2.applies_to) else r2


def effective_conflict(r1: Rule, r2: Rule) -> bool:
    """Return True if two rules for the same additive have different effective dates."""
    return r1.additive == r2.additive and r1.effective != r2.effective


def preemption_status(state_rule: Rule | None, fed_rule: Rule | None) -> str:
    """Classify the relationship between a state rule and a federal rule."""
    if state_rule and not fed_rule:
        return "STATE_ONLY"
    if fed_rule and not state_rule:
        return "FEDERAL_ONLY"
    if not state_rule and not fed_rule:
        return "NONE"
    assert state_rule is not None and fed_rule is not None
    if state_rule.effective < fed_rule.effective:
        return "STATE_EARLIER"
    if fed_rule.effective < state_rule.effective:
        return "FEDERAL_EARLIER"
    return "CO_EXTENSIVE"


def resolve_conflicts(rules: list[Rule], state: str, at: datetime) -> list[Rule]:
    """Return all rules applicable in state whose effective date is <= at (local wall clock)."""
    st = state.strip().upper()
    wall = at.replace(tzinfo=None)
    applicable = [
        r for r in rules
        if (st in r.jurisdictions or "US" in r.jurisdictions) and r.effective <= wall
    ]
    return sorted(applicable, key=lambda r: (r.effective, r.rule_id))


def preemption_report(rules: list[Rule], state: str) -> dict:
    """Generate a preemption status report across all additives in rules."""
    additives = sorted({r.additive for r in rules})
    by_additive: dict[str, str] = {}
    for add in additives:
        sr = state_rule_for(rules, add, state)
        fr = federal_rule_for(rules, add)
        by_additive[add] = preemption_status(sr, fr)
    return {"state": state.upper(), "additives": by_additive}


def preemption_matrix(rules: list[Rule], states: list[str]) -> dict[str, list[str]]:
    """Map each state to the list of rule_ids applicable in that state."""
    out: dict[str, list[str]] = {}
    for st in states:
        s = st.strip().upper()
        out[s] = sorted(r.rule_id for r in rules if s in r.jurisdictions or "US" in r.jurisdictions)
    return out
