"""Resolve conflicts and preemption between state and federal rules."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from contract import Rule


@dataclass
class PreemptionResolver:
    """Resolver for state and federal regulatory rule overlaps."""

    rules: list[Rule]

    def resolve(self, state: str, at: datetime) -> list[Rule]:
        return resolve_conflicts(self.rules, state, at)


def federal_rule_for(additive: str, rules: list[Rule]) -> list[Rule]:
    """Return all federal ('US') rules for additive."""
    add = additive.upper().strip()
    return [r for r in rules if r.additive.upper() == add and "US" in r.jurisdictions]


def state_rule_for(additive: str, state: str, rules: list[Rule]) -> list[Rule]:
    """Return all state-specific rules for additive and state."""
    add = additive.upper().strip()
    st = state.upper().strip()
    return [r for r in rules if r.additive.upper() == add and st in r.jurisdictions]


def stricter_rule(r1: Rule, r2: Rule) -> Rule:
    """Return whichever rule has the earlier effective date (tie-break by rule_id)."""
    if r1.effective != r2.effective:
        return r1 if r1.effective < r2.effective else r2
    return r1 if r1.rule_id <= r2.rule_id else r2


def effective_conflict(r1: Rule, r2: Rule) -> bool:
    """Return True if two rules cover the same additive and product scope with different effective dates."""
    if r1.additive.upper() != r2.additive.upper():
        return False
    if not (set(r1.applies_to) & set(r2.applies_to)):
        return False
    return r1.effective != r2.effective


def preemption_status(state_rule: Rule, fed_rule: Rule) -> str:
    """Classify the relationship between a state rule and federal rule."""
    if state_rule.effective < fed_rule.effective:
        return "STATE_EARLIER"
    if state_rule.effective == fed_rule.effective:
        return "CONCURRENT"
    return "FEDERAL_EARLIER"


def resolve_conflicts(rules: list[Rule], state: str, at: datetime) -> list[Rule]:
    """Return all rules applicable in state (including US) that are in effect at local time 'at'."""
    st = state.upper().strip()
    wall = at.replace(tzinfo=None)
    active = [
        r
        for r in rules
        if (st in r.jurisdictions or "US" in r.jurisdictions) and wall >= r.effective
    ]
    return sorted(active, key=lambda r: (r.effective, r.rule_id))


def preemption_report(rules: list[Rule], state: str) -> dict:
    """Build a report comparing state rules in state with federal US rules."""
    st_rules = [r for r in rules if state.upper() in r.jurisdictions]
    fed_rules = [r for r in rules if "US" in r.jurisdictions]
    comparisons: list[dict] = []
    for sr in st_rules:
        for fr in fed_rules:
            if sr.additive == fr.additive and (set(sr.applies_to) & set(fr.applies_to)):
                comparisons.append(
                    {
                        "additive": sr.additive,
                        "state_rule": sr.rule_id,
                        "fed_rule": fr.rule_id,
                        "status": preemption_status(sr, fr),
                    }
                )
    return {"state": state.upper(), "comparisons": comparisons}


def preemption_matrix(rules: list[Rule]) -> dict:
    """Return a matrix of additives to their earliest effective rule_id per jurisdiction."""
    matrix: dict[str, dict[str, str]] = {}
    for r in rules:
        bucket = matrix.setdefault(r.additive, {})
        for j in r.jurisdictions:
            bucket[j] = r.rule_id
    return matrix
