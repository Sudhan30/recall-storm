"""Jurisdiction hierarchy and state matching for regulatory rules."""
from __future__ import annotations

from contract import Rule
from recallstorm.core.errors import RuleConfigError

_STATES: dict[str, str] = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "US": "United States",
}


def state_codes() -> tuple[str, ...]:
    """Return sorted 2-letter US state codes."""
    return tuple(sorted(k for k in _STATES if k != "US"))


def state_name(code: str) -> str:
    """Return full state name for a 2-letter code."""
    if not isinstance(code, str) or code.strip().upper() not in _STATES:
        raise RuleConfigError(f"Unknown state or jurisdiction code: {code}")
    return _STATES[code.strip().upper()]


def jurisdictions_for_state(state: str) -> tuple[str, ...]:
    """Return applicable jurisdiction codes for a state: (state, 'US')."""
    if not isinstance(state, str) or not state.strip():
        raise RuleConfigError("state must be a non-empty string")
    st = state.strip().upper()
    if st == "US":
        return ("US",)
    return (st, "US")


def jurisdiction_chain(state: str) -> list[str]:
    """Return ordered jurisdiction hierarchy from most specific to federal."""
    return list(jurisdictions_for_state(state))


def jurisdiction_rank(jur: str) -> int:
    """Return specificity rank of a jurisdiction (state=1, US=2)."""
    return 2 if jur.strip().upper() == "US" else 1


def federal_applies(rule: Rule) -> bool:
    """Return True if rule has 'US' in its jurisdictions."""
    if not isinstance(rule, Rule):
        raise TypeError("rule must be a Rule")
    return "US" in rule.jurisdictions


def applies_in_state(rule: Rule, state: str) -> bool:
    """Return True if rule applies in state (either state-specific or federal 'US')."""
    if not isinstance(rule, Rule):
        raise TypeError("rule must be a Rule")
    allowed = set(jurisdictions_for_state(state))
    return any(j.upper() in allowed for j in rule.jurisdictions)


def state_preempts(rule: Rule, state: str) -> bool:
    """Return True if rule is explicitly enacted by the target state."""
    if not isinstance(rule, Rule):
        raise TypeError("rule must be a Rule")
    st = state.strip().upper()
    return st != "US" and st in (j.upper() for j in rule.jurisdictions)


def resolve_jurisdictions(rules: list[Rule], state: str) -> list[Rule]:
    """Filter and sort rules applicable in state, state-specific before federal."""
    matched = [r for r in rules if applies_in_state(r, state)]
    return sorted(
        matched,
        key=lambda r: (min(jurisdiction_rank(j) for j in r.jurisdictions), r.effective, r.rule_id),
    )
