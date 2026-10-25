"""GS1 and openFDA lot-based recall scenario builder."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

from contract import DataPack, Rule, Sku
from recallstorm.gs1.match import match_recall_to_skus
from recallstorm.ingest.openfda_enforcement import parse_enforcement_report
from recallstorm.plan.assemble import assemble_plan


@dataclass
class Gs1Scenario:
    """GS1 / openFDA lot-based recall scenario."""

    scenario_id: str
    recall_number: str
    state: str
    gtins: list[str] = field(default_factory=list)
    lots: list[str] = field(default_factory=list)
    as_of: str = "2026-12-30T18:00:00-08:00"
    deadline: str = "2027-01-01T00:00:00-08:00"


def load_gs1_scenario(path_or_dict: str | dict) -> Gs1Scenario:
    """Load a Gs1Scenario from a JSON file path or dictionary."""
    if isinstance(path_or_dict, str):
        data = json.loads(Path(path_or_dict).read_text(encoding="utf-8"))
    else:
        data = dict(path_or_dict)
    return Gs1Scenario(
        scenario_id=str(data.get("scenario_id", "gs1_recall")),
        recall_number=str(data.get("recall_number", "F-0001-2026")),
        state=str(data.get("state", "CA")),
        gtins=[str(g).zfill(14) for g in data.get("gtins", [])],
        lots=[str(l) for l in data.get("lots", [])],
        as_of=str(data.get("as_of", "2026-12-30T18:00:00-08:00")),
        deadline=str(data.get("deadline", "2027-01-01T00:00:00-08:00")),
    )


def recall_from_openfda(rep: dict) -> Gs1Scenario:
    """Convert an openFDA enforcement report dictionary into a Gs1Scenario."""
    parsed = parse_enforcement_report(rep)
    st = parsed["jurisdictions"][0] if parsed["jurisdictions"] else "US"
    return Gs1Scenario(
        scenario_id=f"openfda_{parsed['recall_number']}",
        recall_number=parsed["recall_number"],
        state=st,
        gtins=parsed["gtins"],
        lots=parsed["lots"],
    )


def recall_skus(scenario: Gs1Scenario, skus: list[Sku]) -> list[Sku]:
    """Return Skus matching the scenario's GTINs."""
    return match_recall_to_skus({"gtins": scenario.gtins, "title": ""}, skus)


def recall_lots(scenario: Gs1Scenario) -> list[str]:
    """Return the affected lot codes for scenario."""
    return list(scenario.lots)


def recall_window(scenario: Gs1Scenario) -> tuple[str, str]:
    """Return (as_of, deadline) window for scenario."""
    return (scenario.as_of, scenario.deadline)


def recall_rule(scenario: Gs1Scenario) -> Rule:
    """Synthesize a contract Rule corresponding to the GS1 recall scenario."""
    eff = datetime.fromisoformat(scenario.as_of).replace(tzinfo=None)
    return Rule(
        rule_id=f"GS1_{scenario.recall_number}",
        additive="RED3",
        aliases=("FD&C Red No. 3", "Red 3", "E127"),
        jurisdictions=(scenario.state, "US"),
        applies_to=("food",),
        effective=eff,
        clause_ref=f"openFDA {scenario.recall_number}",
        source_text=f"Recall {scenario.recall_number} for lots {scenario.lots}",
    )


def recall_plan(scenario: Gs1Scenario, pack: DataPack) -> list[dict]:
    """Assemble a full execution plan for a Gs1Scenario."""
    sc_dict = {
        "scenario_id": scenario.scenario_id,
        "state": scenario.state,
        "rule_ids": [r.rule_id for r in pack.rules],
        "as_of": scenario.as_of,
        "deadline": scenario.deadline,
    }
    return assemble_plan(pack, sc_dict)


def gs1_scenario_summary(scenario: Gs1Scenario) -> dict:
    """Summarize a Gs1Scenario."""
    return {
        "scenario_id": scenario.scenario_id,
        "recall_number": scenario.recall_number,
        "gtin_count": len(scenario.gtins),
        "lot_count": len(scenario.lots),
    }
