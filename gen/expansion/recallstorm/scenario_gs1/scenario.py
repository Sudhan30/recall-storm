"""GS1 lot-code recall scenario builder driven by openFDA enforcement reports."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from contract import DataPack, Rule, Sku
from recallstorm.gs1.lots import normalize_lot
from recallstorm.gs1.match import match_recall_to_skus
from recallstorm.ingest.openfda_enforcement import enforcement_to_recall


@dataclass(frozen=True)
class Gs1Scenario:
    """Lot-level GS1 recall scenario definition."""

    scenario_id: str
    recall_id: str
    state: str
    gtins: tuple[str, ...]
    lot_codes: tuple[str, ...]
    as_of: str
    deadline: str
    reason: str = "openFDA lot recall"


def recall_from_openfda(report: dict) -> Gs1Scenario:
    """Build a Gs1Scenario from a raw openFDA enforcement report dictionary."""
    rec = enforcement_to_recall(report)
    st = rec["states"][0] if rec.get("states") and rec["states"][0] != "US" else "CA"
    lots = tuple(normalize_lot(l) for l in rec.get("lot_codes", [])) or ("LOT2026A",)
    return Gs1Scenario(
        scenario_id=f"gs1_{rec['recall_id'].lower().replace('-', '_')}",
        recall_id=rec["recall_id"],
        state=st,
        gtins=tuple(rec.get("gtins", [])),
        lot_codes=lots,
        as_of="2026-12-30T18:00:00-08:00",
        deadline="2027-01-01T00:00:00-08:00",
        reason=rec.get("reason", "openFDA enforcement"),
    )


def load_gs1_scenario(raw_or_path: dict | str | Path) -> Gs1Scenario:
    """Load a Gs1Scenario from a JSON file path or dictionary."""
    if isinstance(raw_or_path, (str, Path)):
        raw = json.loads(Path(raw_or_path).read_text(encoding="utf-8"))
    elif isinstance(raw_or_path, dict):
        raw = raw_or_path
    else:
        raise TypeError("Expected dict or path")
    if "recall_number" in raw and "scenario_id" not in raw:
        return recall_from_openfda(raw)
    return Gs1Scenario(
        scenario_id=str(raw.get("scenario_id", "gs1_lot_recall")),
        recall_id=str(raw.get("recall_id", "F-0100-2026")),
        state=str(raw.get("state", "CA")),
        gtins=tuple(str(g) for g in raw.get("gtins", [])),
        lot_codes=tuple(normalize_lot(str(l)) for l in raw.get("lot_codes", ["LOT2026A"])),
        as_of=str(raw.get("as_of", "2026-12-30T18:00:00-08:00")),
        deadline=str(raw.get("deadline", "2027-01-01T00:00:00-08:00")),
        reason=str(raw.get("reason", "GS1 lot recall")),
    )


def recall_skus(scenario: Gs1Scenario, skus: list[Sku]) -> list[Sku]:
    """Return catalog SKUs matching the Gs1Scenario's GTINs."""
    rec_dict = {"gtins": list(scenario.gtins), "title": scenario.reason}
    return match_recall_to_skus(rec_dict, skus)


def recall_lots(scenario: Gs1Scenario) -> list[str]:
    """Return normalized lot codes targeted by the Gs1Scenario."""
    return list(scenario.lot_codes)


def recall_window(scenario: Gs1Scenario) -> tuple[datetime, datetime]:
    """Return (as_of, deadline) datetimes for the Gs1Scenario."""
    return datetime.fromisoformat(scenario.as_of), datetime.fromisoformat(scenario.deadline)


def recall_rule(scenario: Gs1Scenario) -> Rule:
    """Synthesize a contract Rule representing the openFDA lot recall."""
    eff = datetime.fromisoformat(scenario.as_of).replace(tzinfo=None)
    return Rule(
        rule_id=f"OPENFDA_{scenario.recall_id}",
        additive="RED3",
        aliases=("FD&C Red No. 3", "Red 3", "E127"),
        jurisdictions=(scenario.state, "US"),
        applies_to=("food", "ingested_drug"),
        effective=eff,
        clause_ref=f"openFDA Enforcement {scenario.recall_id}",
        source_text=scenario.reason,
    )


def recall_plan(scenario: Gs1Scenario, pack: DataPack) -> list[dict]:
    """Generate a lot-targeted recall plan for a Gs1Scenario and DataPack."""
    from recallstorm.scenario_gs1.lot_pull import lot_evidence, lot_pull_tasks
    matched = recall_skus(scenario, pack.skus)
    target_ids = {s.sku_id for s in matched}
    win = [scenario.as_of, "2026-12-31T06:00:00-08:00"]
    records: list[dict] = []
    for s in matched:
        for lot in scenario.lot_codes:
            records.append(lot_evidence(s.sku_id, lot, scenario.recall_id))
    for st in pack.stores:
        records.extend(
            lot_pull_tasks(st.store_id, pack.facings, target_ids, list(scenario.lot_codes), f"{st.store_id}-A00", win)
        )
    return records


def gs1_scenario_summary(scenario: Gs1Scenario) -> dict:
    """Summarize a Gs1Scenario."""
    return {
        "scenario_id": scenario.scenario_id,
        "recall_id": scenario.recall_id,
        "gtin_count": len(scenario.gtins),
        "lot_codes": list(scenario.lot_codes),
    }
