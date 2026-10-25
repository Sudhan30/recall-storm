"""RuleSet container, JSONL loading, filtering, and hashing."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from contract import Rule
from recallstorm.core.clock import from_local
from recallstorm.core.errors import RuleConfigError
from recallstorm.core.jsonl import read_jsonl


@dataclass(frozen=True)
class RuleSet:
    """Immutable collection of regulatory Rules."""

    rules: tuple[Rule, ...]


def load_rules(path_or_list: str | Path | list[Rule] | list[dict]) -> RuleSet:
    """Load a RuleSet from a JSONL path, list of Rule objects, or list of dicts."""
    if isinstance(path_or_list, (str, Path)):
        raw_list = read_jsonl(path_or_list)
    elif isinstance(path_or_list, list):
        raw_list = path_or_list
    else:
        raise RuleConfigError("Expected path or list for load_rules")

    parsed: list[Rule] = []
    for item in raw_list:
        if isinstance(item, Rule):
            parsed.append(item)
        elif isinstance(item, dict):
            eff = item["effective"]
            eff_dt = datetime.fromisoformat(eff) if isinstance(eff, str) else eff
            parsed.append(
                Rule(
                    rule_id=str(item["rule_id"]),
                    additive=str(item["additive"]),
                    aliases=tuple(str(a) for a in item["aliases"]),
                    jurisdictions=tuple(str(j) for j in item["jurisdictions"]),
                    applies_to=tuple(str(ap) for ap in item["applies_to"]),
                    effective=eff_dt.replace(tzinfo=None),
                    clause_ref=str(item["clause_ref"]),
                    source_text=str(item["source_text"]),
                )
            )
        else:
            raise RuleConfigError(f"Unsupported rule item: {type(item)}")
    return RuleSet(rules=tuple(parsed))


def rule_by_id(ruleset: RuleSet | list[Rule], rule_id: str) -> Rule:
    """Retrieve a Rule by its rule_id."""
    rlist = ruleset.rules if isinstance(ruleset, RuleSet) else ruleset
    for r in rlist:
        if r.rule_id == rule_id:
            return r
    raise RuleConfigError(f"Rule not found: {rule_id}")


def rules_for_state(ruleset: RuleSet | list[Rule], state: str) -> list[Rule]:
    """Return rules applicable in the given 2-letter state (including 'US' federal rules)."""
    st = state.strip().upper()
    rlist = ruleset.rules if isinstance(ruleset, RuleSet) else ruleset
    return [r for r in rlist if st in r.jurisdictions or "US" in r.jurisdictions]


def rules_for_additive(ruleset: RuleSet | list[Rule], additive: str) -> list[Rule]:
    """Return rules targeting a specific additive."""
    add = additive.strip().upper()
    rlist = ruleset.rules if isinstance(ruleset, RuleSet) else ruleset
    return [r for r in rlist if r.additive.upper() == add]


def rules_for_product_type(ruleset: RuleSet | list[Rule], prod_type: str) -> list[Rule]:
    """Return rules whose applies_to includes prod_type ('food', 'ingested_drug', 'cosmetic')."""
    pt = prod_type.strip().lower()
    rlist = ruleset.rules if isinstance(ruleset, RuleSet) else ruleset
    return [r for r in rlist if pt in r.applies_to]


def effective_local(rule: Rule, tz_name: str = "America/Los_Angeles") -> datetime:
    """Attach a store timezone to a Rule's naive wall-clock effective datetime."""
    if not isinstance(rule, Rule):
        raise TypeError("rule must be a Rule")
    return from_local(rule.effective.replace(tzinfo=None), tz_name)


def rule_summary(rule: Rule) -> dict:
    """Return a concise dictionary summary of a Rule."""
    return {
        "rule_id": rule.rule_id,
        "additive": rule.additive,
        "jurisdictions": list(rule.jurisdictions),
        "applies_to": list(rule.applies_to),
        "effective": rule.effective.isoformat(),
        "clause_ref": rule.clause_ref,
    }


def ruleset_hash(ruleset: RuleSet | list[Rule]) -> str:
    """Compute a deterministic SHA-256 hash of a RuleSet."""
    rlist = ruleset.rules if isinstance(ruleset, RuleSet) else ruleset
    payload = json.dumps([rule_summary(r) for r in sorted(rlist, key=lambda x: x.rule_id)], sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
