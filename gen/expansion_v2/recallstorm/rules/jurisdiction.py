"""Jurisdiction hierarchy and state/federal applicability."""
from __future__ import annotations

from contract import Rule

_STATE_NAMES: dict[str, str] = {
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
    "DC": "District of Columbia", "US": "United States",
}


def state_codes() -> tuple[str, ...]:
    """Return tuple of valid two-letter state/jurisdiction codes."""
    return tuple(sorted(_STATE_NAMES.keys()))


def state_name(code: str) -> str:
    """Return the full state name for a two-letter code."""
    c = (code or "").upper().strip()
    if c not in _STATE_NAMES:
        raise ValueError(f"Unknown state code: {code!r}")
    return _STATE_NAMES[c]


def jurisdictions_for_state(state: str) -> tuple[str, ...]:
    """Return applicable jurisdictions for a state (e.g. ('CA', 'US'))."""
    st = (state or "").upper().strip()
    if not st:
        raise ValueError("state cannot be empty")
    if st == "US":
        return ("US",)
    return (st, "US")


def jurisdiction_chain(state: str) -> list[str]:
    """Return ordered list of jurisdictions from most specific (state) to broadest ('US')."""
    return list(jurisdictions_for_state(state))


def federal_applies(rule: Rule) -> bool:
    """Return True if rule includes 'US' in its jurisdictions."""
    return "US" in rule.jurisdictions


def applies_in_state(rule: Rule, state: str) -> bool:
    """Return True if rule applies in state (either via state code or 'US')."""
    valid = set(jurisdictions_for_state(state))
    return bool(valid & set(rule.jurisdictions))


def state_preempts(state_rule: Rule, fed_rule: Rule) -> bool:
    """Return True if state_rule takes effect earlier than fed_rule."""
    return state_rule.effective < fed_rule.effective


def jurisdiction_rank(jur: str) -> int:
    """Return specificity rank (1 for state, 2 for federal 'US')."""
    return 2 if jur.upper().strip() == "US" else 1


def resolve_jurisdictions(rules: list[Rule], state: str) -> list[Rule]:
    """Filter rules to those applicable in state, ordered by state-specific first then effective date."""
    matching = [r for r in rules if applies_in_state(r, state)]
    return sorted(
        matching,
        key=lambda r: (min(jurisdiction_rank(j) for j in r.jurisdictions), r.effective, r.rule_id),
    )
