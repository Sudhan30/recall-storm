"""Recall Storm contract. Frozen before the core run. Do not edit after the expansion launches."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Protocol

# ---------- vocabulary (D3 checks every uppercase code against these) ----------
class Verdict(str, Enum):
    PULL = "PULL"; HOLD_VERIFY = "HOLD_VERIFY"; KEEP = "KEEP"

class Action(str, Enum):
    PULL = "PULL"; HOLD_VERIFY = "HOLD_VERIFY"; PLACE_SUB = "PLACE_SUB"; TAG_FLASH = "TAG_FLASH"

class StoreFormat(str, Enum):
    SUPERCENTER = "SUPERCENTER"; DISCOUNT = "DISCOUNT"; NEIGHBORHOOD = "NEIGHBORHOOD"; SAMS = "SAMS"

class ExceptionKind(str, Enum):
    DSD_VENDOR_PULL = "DSD_VENDOR_PULL"; ENDCAP_DISPLAY = "ENDCAP_DISPLAY"; TOPSTOCK = "TOPSTOCK"
    PICKUP_TOTES = "PICKUP_TOTES"; NOT_ON_PLANOGRAM = "NOT_ON_PLANOGRAM"; UNCLEAR_LABEL = "UNCLEAR_LABEL"

class HandoffKind(str, Enum):
    FLOATER = "FLOATER"; SUB_TRANSFER = "SUB_TRANSFER"; RETURN_CONSOLIDATION = "RETURN_CONSOLIDATION"

class DecidedBy(str, Enum):
    RULE = "RULE"; MODEL = "MODEL"

# ---------- input data ----------
@dataclass(frozen=True)
class Sku:
    sku_id: str; gtin: str; name: str; brand: str; category: str; ingredients: str
    is_food: bool; is_ingested_drug: bool; case_units: int; case_cube_ft3: float; case_weight_lb: float

@dataclass(frozen=True)
class Store:
    store_id: str; format: StoreFormat; state: str; city: str; lat: float; lon: float
    district: str; dc_id: str; tz: str            # tz like "America/Los_Angeles"

@dataclass(frozen=True)
class Location:
    aisle: str; bay: int; shelf: int; pos: int

@dataclass(frozen=True)
class Facing:
    store_id: str; sku_id: str; loc: Location; units: int

@dataclass(frozen=True)
class Associate:
    associate_id: str; store_id: str | None; district: str; is_floater: bool
    shift_start: datetime; shift_end: datetime     # local time, tz-aware

@dataclass(frozen=True)
class Truck:
    truck_id: str; dc_id: str; cube_ft3: float; weight_lb: float; depart: datetime

@dataclass(frozen=True)
class DcStock:
    dc_id: str; sku_id: str; cases: int

@dataclass(frozen=True)
class StoreNote:
    note_id: str; store_id: str; text: str          # free text; exceptions come from here

@dataclass(frozen=True)
class Rule:
    rule_id: str; additive: str; aliases: tuple[str, ...]; jurisdictions: tuple[str, ...]
    applies_to: tuple[str, ...]                     # "food", "ingested_drug", "cosmetic"
    effective: datetime                             # sale prohibited at or after this instant, local
    clause_ref: str; source_text: str

@dataclass
class DataPack:
    skus: list[Sku]; stores: list[Store]; facings: list[Facing]; associates: list[Associate]
    trucks: list[Truck]; dc_stock: list[DcStock]; substitutes: dict[str, list[str]]
    notes: list[StoreNote]; rules: list[Rule]; as_of: datetime

def load_datapack(data_dir: str) -> DataPack:
    """Loads data/*.jsonl into a DataPack. Implemented by us in contract_io.py (not generated)."""
    from contract_io import load  # ours
    return load(data_dir)

# ---------- outputs of the matched packages (acceptance tests target these) ----------
@dataclass(frozen=True)
class SkuDecision:
    sku_id: str; verdict: Verdict; additive: str | None; match_text: str | None
    match_start: int | None; match_end: int | None; rule_ids: tuple[str, ...]
    decided_by: DecidedBy; rationale: str

@dataclass(frozen=True)
class Allocation:
    alloc_id: str; dc_id: str; sub_sku_id: str; store_id: str; qty_cases: int; dc_balance_after: int

@dataclass(frozen=True)
class Stop:
    store_id: str; cases: int; cube_ft3: float; weight_lb: float

@dataclass(frozen=True)
class RouteManifest:
    manifest_id: str; truck_id: str; dc_id: str; stops: tuple[Stop, ...]; depart: datetime

class Classifier(Protocol):
    """Gemini hook for items rules cannot decide. Returns HOLD_VERIFY when unsure."""
    def __call__(self, sku: Sku, candidates: list[Rule]) -> SkuDecision: ...

# rules package MUST expose:
def evaluate_sku(sku: Sku, rules: list[Rule], state: str, at: datetime,
                 classifier: Classifier | None = None) -> SkuDecision: ...
# allocate package MUST expose (never exceed stock; integer cases; deterministic tie-breaks by store_id):
def allocate_substitutes(demand: dict[tuple[str, str], int],      # (store_id, sub_sku_id) -> cases wanted
                         stock: list[DcStock], stores: list[Store]) -> list[Allocation]: ...
# route package MUST expose (cube and weight within truck limits; every pulled case on exactly one stop):
def pack_returns(pulled_cases: dict[tuple[str, str], int],         # (store_id, sku_id) -> cases
                 skus: list[Sku], trucks: list[Truck], stores: list[Store]) -> list[RouteManifest]: ...

# ---------- plan.jsonl record types and required fields ----------
PLAN_TYPES: dict[str, tuple[str, ...]] = {
    "run":            ("run_id", "scenario_id", "generator", "as_of", "rule_ids", "src"),
    "sku_verdict":    ("sku_id", "gtin", "verdict", "additive", "match", "rule_ids", "jurisdictions",
                       "decided_by", "evidence_id", "src"),
    "evidence":       ("evidence_id", "sku_id", "rule_id", "clause_ref", "source_span", "rationale", "src"),
    "store_playbook": ("store_id", "format", "deadline", "windows", "counts", "associate_ids",
                       "exception_ids", "manifest_ids", "src"),
    "shelf_task":     ("task_id", "store_id", "sku_id", "action", "loc", "qty_units", "associate_id",
                       "window", "seq", "evidence_id", "sub_sku_id", "alloc_id", "src"),
    "exception":      ("exc_id", "store_id", "kind", "note_id", "resolution", "task_ids", "src"),
    "allocation":     ("alloc_id", "dc_id", "sub_sku_id", "store_id", "qty_cases", "dc_balance_after", "src"),
    "handoff":        ("handoff_id", "kind", "from_id", "to_id", "window", "qty", "ref_ids", "src"),
    "route_manifest": ("manifest_id", "truck_id", "dc_id", "stops", "limits", "depart", "src"),
}
# src = repo-relative path of the module that emitted the record. Windows are ISO local times [start, end].
# CLI contract: python -m recallstorm run --scenario <id> --data data/ --out out/<name>/
#   writes out/<name>/plan.jsonl and out/<name>/events.jsonl
# events.jsonl: {"t": iso, "store_id", "associate_id", "kind": "MOVE"|"PULL"|"PLACE"|"DONE", "loc", "task_id"}
