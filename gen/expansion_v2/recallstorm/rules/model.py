"""RuleSet container and rule query helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json

from contract import Rule
from recallstorm.core.clock import from_local
from recallstorm.core.jsonl import read_jsonl


@dataclass
class RuleSet:
    """Indexed collection of regulatory Rules."""

    rules: list[Rule] = field(default_factory=list)


def _as_list(rules: list[Rule] | RuleSet) -> list[Rule]:
    return rules.rules if isinstance(rules, RuleSet) else list(rules)


def load_rules(path: str) -> RuleSet:
    """Load rules from a rules.jsonl file into a RuleSet."""
    rows = read_jsonl(path)
    parsed: list[Rule] = []
    for r in rows:
        parsed.append(
            Rule(
                rule_id=str(r["rule_id"]),
                additive=str(r["additive"]),
                aliases=tuple(str(x) for x in r["aliases"]),
                jurisdictions=tuple(str(x) for x in r["jurisdictions"]),
                applies_to=tuple(str(x) for x in r["applies_to"]),
                effective=datetime.fromisoformat(str(r["effective"])).replace(tzinfo=None),
                clause_ref=str(r["clause_ref"]),
                source_text=str(r["source_text"]),
            )
        )
    return RuleSet(parsed)


def rule_by_id(rules: list[Rule] | RuleSet, rule_id: str) -> Rule | None:
    """Find a Rule by rule_id, or return None."""
    for r in _as_list(rules):
        if r.rule_id == rule_id:
            return r
    return None


def rules_for_state(rules: list[Rule] | RuleSet, state: str) -> list[Rule]:
    """Return rules applicable in state (matching state or 'US')."""
    st = state.upper().strip()
    return [r for r in _as_list(rules) if st in r.jurisdictions or "US" in r.jurisdictions]


def rules_for_additive(rules: list[Rule] | RuleSet, additive: str) -> list[Rule]:
    """Return rules targeting a specific additive."""
    add = additive.upper().strip()
    return [r for r in _as_list(rules) if r.additive.upper() == add]


def rules_for_product_type(rules: list[Rule] | RuleSet, ptype: str) -> list[Rule]:
    """Return rules whose applies_to includes ptype ('food', 'ingested_drug', 'cosmetic')."""
    pt = ptype.lower().strip()
    return [r for r in _as_list(rules) if pt in r.applies_to]


def effective_local(rule: Rule, tz_name: str = "America/Los_Angeles") -> datetime:
    """Attach a store's local timezone to rule.effective."""
    return from_local(rule.effective, tz_name)


def rule_summary(rule: Rule) -> dict:
    """Return a serializable dictionary summary of a Rule."""
    return {
        "rule_id": rule.rule_id,
        "additive": rule.additive,
        "jurisdictions": list(rule.jurisdictions),
        "applies_to": list(rule.applies_to),
        "effective": rule.effective.isoformat(),
        "clause_ref": rule.clause_ref,
    }


def ruleset_hash(rules: list[Rule] | RuleSet) -> str:
    """Return a deterministic SHA-256 hash of a RuleSet."""
    payload = [rule_summary(r) for r in sorted(_as_list(rules), key=lambda x: x.rule_id)]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]
