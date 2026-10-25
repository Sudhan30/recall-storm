You are expanding Recall Storm into a full platform in ONE continued generation.
contract.py is frozen and already exists. Everything you write must use it unchanged.

Write these packages in this exact order (positions matter for our measurements):
core/ (ID scheme, errors, config, logging) -> ingest/ (USDA FDC, Open Food Facts, openFDA enforcement, CPSC,
store list parsers) -> aliases/ -> rules/ (FDA Red No. 3 food and drug, CA AB 418 four additives, BVO,
Minnesota PFAS 116.943, CARB multi-purpose lubricant VOC; jurisdiction and date engine) -> adjudicate/ ->
gs1/ (GTIN check digits, AI 01/10/17, Digital Link, recall lot and date-range matching) -> store/ -> labor/ ->
allocate/ -> plan/ -> sim/ -> gs1-based recall scenario (openFDA lot codes) -> route/ (LAST package) -> cli/ ->
tests/integration/ (cross-package and property tests) -> docs/.
Each package is followed by its unit tests. route/ must be the last package before cli/.

For every package, implement the full public API listed in the manifest you write, with docstrings,
input validation, and error handling. Integration tests must exercise modules from every earlier package.


Required public APIs carried over from contract.py (the acceptance tests import exactly these):
- recallstorm/rules/:    evaluate_sku(sku, rules, state, at, classifier=None) -> SkuDecision
- recallstorm/allocate/: allocate_substitutes(demand, stock, stores) -> list[Allocation]
- recallstorm/route/:    pack_returns(pulled_cases, skus, trucks, stores) -> list[RouteManifest]
- recallstorm/__main__.py: python -m recallstorm run --scenario ID --data DIR --out DIR
Later packages must import and call earlier packages by the exact names declared in your manifest.

CONVENTIONS (facts about the environment you are writing into)
- contract.py and contract_io.py exist at the repo root. Import with `from contract import ...`.
  Load data with `from contract import load_datapack; pack = load_datapack(data_dir)`.
- Rule.effective is a NAIVE wall-clock datetime, interpreted in each store's local tz (Store.tz).
  `at` passed to evaluate_sku is tz-aware; compare at.astimezone(ZoneInfo(store_tz)).replace(tzinfo=None)
  against rule.effective when you know the tz, else at.replace(tzinfo=None). Sale is prohibited when
  local(at) >= effective. evaluate_sku with state="CA" applies rules whose jurisdictions include "CA" or "US".
- Datetimes in plan.jsonl and events.jsonl are ISO 8601 with offset.
- The scenario file is data/scenario_<id>.json (fields: scenario_id, state, rule_ids, as_of, deadline).
- The deadline for every task window is the scenario deadline; windows must end strictly before it.
- data/labels.csv is ground truth and you will NOT see it. Do not read it from code.


=== contract.py ===
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


=== data/rules.jsonl ===
{"rule_id": "CA_AB418_RED3", "additive": "RED3", "aliases": ["FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"], "jurisdictions": ["CA"], "applies_to": ["food"], "effective": "2027-01-01T00:00:00", "clause_ref": "Cal. Health & Safety Code 109025(a)", "source_text": "Commencing January 1, 2027, a person or entity shall not manufacture, sell, deliver, distribute, hold, or offer for sale, in commerce a food product for human consumption that contains any of the following substances: (1) Brominated vegetable oil. (2) Potassium bromate. (3) Propylparaben. (4) Red dye 3."}
{"rule_id": "FDA_RED3_FOOD", "additive": "RED3", "aliases": ["FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"], "jurisdictions": ["US"], "applies_to": ["food"], "effective": "2027-01-15T00:00:00", "clause_ref": "21 CFR 74.303 (revoked for food, 90 FR 4628)", "source_text": "FDA is revoking the authorization for the use of FD&C Red No. 3 in food and ingested drugs. Manufacturers who use FD&C Red No. 3 in food have until January 15, 2027 to reformulate their products."}
{"rule_id": "FDA_RED3_DRUG", "additive": "RED3", "aliases": ["FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127"], "jurisdictions": ["US"], "applies_to": ["ingested_drug"], "effective": "2028-01-18T00:00:00", "clause_ref": "21 CFR 74.1303 (revoked for ingested drugs, 90 FR 4628)", "source_text": "Manufacturers of ingested drugs have until January 18, 2028 to reformulate."}


=== data/scenario_ca_red3.json ===
{
  "scenario_id": "ca_red3",
  "state": "CA",
  "rule_ids": [
    "CA_AB418_RED3"
  ],
  "as_of": "2026-12-30T18:00:00-08:00",
  "deadline": "2027-01-01T00:00:00-08:00",
  "note": "every window must end before 2027-01-01T00:00 local"
}


=== data/skus.jsonl (20 sample rows) ===
{"sku_id": "SKU00000", "gtin": "00078000000009", "name": "Candy FD&C #0", "brand": "Kandy Co", "category": "candy", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, FD&C Red No. 3, red 40", "is_food": true, "is_ingested_drug": false, "case_units": 24, "case_cube_ft3": 1.4, "case_weight_lb": 7.1}
{"sku_id": "SKU00009", "gtin": "00078000000092", "name": "Gummies erythros1ne #0", "brand": "Brite", "category": "gummies", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, erythros1ne, red 40", "is_food": true, "is_ingested_drug": false, "case_units": 6, "case_cube_ft3": 1.01, "case_weight_lb": 8.9}
{"sku_id": "SKU00018", "gtin": "00078000000184", "name": "Frosting unclear #0", "brand": "Kandy Co", "category": "frosting", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, color added", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 0.57, "case_weight_lb": 7.8}
{"sku_id": "SKU00027", "gtin": "00078000000276", "name": "Candy FD&C #1", "brand": "Great Value", "category": "candy", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, FD&C RED #3, red 40", "is_food": true, "is_ingested_drug": false, "case_units": 24, "case_cube_ft3": 0.97, "case_weight_lb": 13.8}
{"sku_id": "SKU00036", "gtin": "00078000000368", "name": "Snacks decoy #1", "brand": "Sweetly", "category": "snacks", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, 3 red apples", "is_food": true, "is_ingested_drug": false, "case_units": 24, "case_cube_ft3": 0.55, "case_weight_lb": 13.6}
{"sku_id": "SKU00045", "gtin": "00078000000450", "name": "Sprinkles Red #2", "brand": "Great Value", "category": "sprinkles", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, Red Dye 3, red 40", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.13, "case_weight_lb": 12.5}
{"sku_id": "SKU00054", "gtin": "00078000000542", "name": "Candy decoy #2", "brand": "Brite", "category": "candy", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, Red 40", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.44, "case_weight_lb": 21.2}
{"sku_id": "SKU00063", "gtin": "00078000000634", "name": "Cherry Lip Tint", "brand": "Kandy Co", "category": "cosmetic", "ingredients": "castor oil, red 3", "is_food": false, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 0.52, "case_weight_lb": 11.5}
{"sku_id": "SKU00072", "gtin": "00078000000726", "name": "Beverages control #6", "brand": "Sweetly", "category": "beverages", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, salt", "is_food": true, "is_ingested_drug": false, "case_units": 6, "case_cube_ft3": 0.76, "case_weight_lb": 8.5}
{"sku_id": "SKU00081", "gtin": "00078000000818", "name": "Frozen control #15", "brand": "Member's Mark", "category": "frozen", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, salt", "is_food": true, "is_ingested_drug": false, "case_units": 24, "case_cube_ft3": 1.38, "case_weight_lb": 16.0}
{"sku_id": "SKU00090", "gtin": "00078000000900", "name": "Baking control #24", "brand": "Great Value", "category": "baking", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, salt", "is_food": true, "is_ingested_drug": false, "case_units": 6, "case_cube_ft3": 0.64, "case_weight_lb": 7.5}
{"sku_id": "SKU00099", "gtin": "00078000000993", "name": "Candy control #33", "brand": "Member's Mark", "category": "candy", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, salt", "is_food": true, "is_ingested_drug": false, "case_units": 24, "case_cube_ft3": 0.58, "case_weight_lb": 10.2}
{"sku_id": "SKU00108", "gtin": "00078000001082", "name": "Candy control #42", "brand": "Kandy Co", "category": "candy", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, salt", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.14, "case_weight_lb": 6.9}
{"sku_id": "SKU00117", "gtin": "00078000001174", "name": "Baking control #51", "brand": "Sweetly", "category": "baking", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, salt", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.58, "case_weight_lb": 12.2}
{"sku_id": "SKU00126", "gtin": "00078000001266", "name": "Frozen control #60", "brand": "Member's Mark", "category": "frozen", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, salt", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.29, "case_weight_lb": 14.7}
{"sku_id": "SKU00135", "gtin": "00078000001358", "name": "Frozen control #69", "brand": "Member's Mark", "category": "frozen", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, salt", "is_food": true, "is_ingested_drug": false, "case_units": 6, "case_cube_ft3": 0.8, "case_weight_lb": 21.3}
{"sku_id": "SKU00144", "gtin": "00078000001440", "name": "Cereal control #78", "brand": "Member's Mark", "category": "cereal", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, salt", "is_food": true, "is_ingested_drug": false, "case_units": 6, "case_cube_ft3": 1.54, "case_weight_lb": 9.2}
{"sku_id": "SKU00153", "gtin": "00078000001532", "name": "Baking control #87", "brand": "Kandy Co", "category": "baking", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, salt", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.25, "case_weight_lb": 8.8}
{"sku_id": "SKU00162", "gtin": "00078000001624", "name": "Frozen control #96", "brand": "Brite", "category": "frozen", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, salt", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.6, "case_weight_lb": 5.7}
{"sku_id": "SKU00171", "gtin": "00078000001716", "name": "Candy control #105", "brand": "Great Value", "category": "candy", "ingredients": "sugar, corn syrup, water, citric acid, natural flavor, salt", "is_food": true, "is_ingested_drug": false, "case_units": 6, "case_cube_ft3": 1.83, "case_weight_lb": 18.1}

=== data/stores.jsonl (20 sample rows) ===
{"store_id": "CA1000", "format": "SUPERCENTER", "state": "CA", "city": "Sacramento", "lat": 38.5623, "lon": -121.5287, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1001", "format": "SUPERCENTER", "state": "CA", "city": "Fresno", "lat": 36.7042, "lon": -119.7718, "district": "D01", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles"}
{"store_id": "CA1002", "format": "SUPERCENTER", "state": "CA", "city": "Los Angeles", "lat": 34.0234, "lon": -118.2118, "district": "D01", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1003", "format": "SUPERCENTER", "state": "CA", "city": "San Diego", "lat": 32.6742, "lon": -117.1724, "district": "D01", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1004", "format": "SUPERCENTER", "state": "CA", "city": "San Jose", "lat": 37.3718, "lon": -121.8809, "district": "D01", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles"}
{"store_id": "CA1005", "format": "SUPERCENTER", "state": "CA", "city": "Bakersfield", "lat": 35.3506, "lon": -118.9786, "district": "D01", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles"}
{"store_id": "CA1006", "format": "SUPERCENTER", "state": "CA", "city": "Riverside", "lat": 33.9635, "lon": -117.3957, "district": "D01", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1007", "format": "SUPERCENTER", "state": "CA", "city": "Stockton", "lat": 37.9105, "lon": -121.331, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1008", "format": "NEIGHBORHOOD", "state": "CA", "city": "Redding", "lat": 40.6288, "lon": -122.3468, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1009", "format": "NEIGHBORHOOD", "state": "CA", "city": "Chico", "lat": 39.6872, "lon": -121.8274, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1010", "format": "NEIGHBORHOOD", "state": "CA", "city": "Modesto", "lat": 37.5921, "lon": -121.0248, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1011", "format": "NEIGHBORHOOD", "state": "CA", "city": "Anaheim", "lat": 33.8005, "lon": -117.8808, "district": "D01", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1012", "format": "NEIGHBORHOOD", "state": "CA", "city": "Oxnard", "lat": 34.25, "lon": -119.1559, "district": "D01", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1013", "format": "DISCOUNT", "state": "CA", "city": "Santa Rosa", "lat": 38.4142, "lon": -122.747, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1014", "format": "DISCOUNT", "state": "CA", "city": "Visalia", "lat": 36.3521, "lon": -119.2963, "district": "D01", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles"}
{"store_id": "CA1015", "format": "DISCOUNT", "state": "CA", "city": "Palmdale", "lat": 34.6277, "lon": -118.074, "district": "D01", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1016", "format": "DISCOUNT", "state": "CA", "city": "Chula Vista", "lat": 32.5977, "lon": -117.1095, "district": "D01", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1017", "format": "SAMS", "state": "CA", "city": "Eureka", "lat": 40.8493, "lon": -124.1851, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles"}
{"store_id": "CA1018", "format": "SAMS", "state": "CA", "city": "Merced", "lat": 37.3444, "lon": -120.451, "district": "D01", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles"}
{"store_id": "CA1019", "format": "SAMS", "state": "CA", "city": "Ontario", "lat": 34.0851, "lon": -117.6821, "district": "D01", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles"}

=== data/facings.jsonl (20 sample rows) ===
{"store_id": "CA1000", "sku_id": "SKU00000", "loc": {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1}, "units": 33}
{"store_id": "CA1000", "sku_id": "SKU00131", "loc": {"aisle": "A01", "bay": 5, "shelf": 2, "pos": 6}, "units": 30}
{"store_id": "CA1001", "sku_id": "SKU00076", "loc": {"aisle": "A01", "bay": 3, "shelf": 3, "pos": 5}, "units": 36}
{"store_id": "CA1002", "sku_id": "SKU00021", "loc": {"aisle": "A01", "bay": 1, "shelf": 4, "pos": 4}, "units": 31}
{"store_id": "CA1002", "sku_id": "SKU00152", "loc": {"aisle": "A02", "bay": 1, "shelf": 1, "pos": 3}, "units": 5}
{"store_id": "CA1003", "sku_id": "SKU00097", "loc": {"aisle": "A01", "bay": 4, "shelf": 2, "pos": 2}, "units": 31}
{"store_id": "CA1004", "sku_id": "SKU00042", "loc": {"aisle": "A01", "bay": 2, "shelf": 3, "pos": 1}, "units": 15}
{"store_id": "CA1004", "sku_id": "SKU00173", "loc": {"aisle": "A02", "bay": 1, "shelf": 4, "pos": 6}, "units": 32}
{"store_id": "CA1005", "sku_id": "SKU00118", "loc": {"aisle": "A01", "bay": 4, "shelf": 5, "pos": 5}, "units": 7}
{"store_id": "CA1006", "sku_id": "SKU00063", "loc": {"aisle": "A01", "bay": 3, "shelf": 1, "pos": 4}, "units": 35}
{"store_id": "CA1007", "sku_id": "SKU00008", "loc": {"aisle": "A01", "bay": 1, "shelf": 2, "pos": 3}, "units": 15}
{"store_id": "CA1007", "sku_id": "SKU00139", "loc": {"aisle": "A01", "bay": 5, "shelf": 4, "pos": 2}, "units": 25}
{"store_id": "CA1008", "sku_id": "SKU00135", "loc": {"aisle": "A01", "bay": 3, "shelf": 5, "pos": 1}, "units": 9}
{"store_id": "CA1009", "sku_id": "SKU00166", "loc": {"aisle": "A01", "bay": 4, "shelf": 3, "pos": 2}, "units": 10}
{"store_id": "CA1011", "sku_id": "SKU00016", "loc": {"aisle": "A01", "bay": 1, "shelf": 2, "pos": 5}, "units": 4}
{"store_id": "CA1012", "sku_id": "SKU00051", "loc": {"aisle": "A01", "bay": 1, "shelf": 5, "pos": 3}, "units": 17}
{"store_id": "CA1013", "sku_id": "SKU00094", "loc": {"aisle": "A01", "bay": 2, "shelf": 4, "pos": 2}, "units": 35}
{"store_id": "CA1014", "sku_id": "SKU00167", "loc": {"aisle": "A01", "bay": 4, "shelf": 1, "pos": 2}, "units": 4}
{"store_id": "CA1016", "sku_id": "SKU00046", "loc": {"aisle": "A01", "bay": 1, "shelf": 4, "pos": 5}, "units": 31}
{"store_id": "CA1017", "sku_id": "SKU00162", "loc": {"aisle": "A01", "bay": 2, "shelf": 4, "pos": 4}, "units": 24}

=== data/associates.jsonl (20 sample rows) ===
{"associate_id": "CA1000-A00", "store_id": "CA1000", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1000-A10", "store_id": "CA1000", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1001-A06", "store_id": "CA1001", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1002-A02", "store_id": "CA1002", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1002-A12", "store_id": "CA1002", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1003-A08", "store_id": "CA1003", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1004-A04", "store_id": "CA1004", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1005-A00", "store_id": "CA1005", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1005-A10", "store_id": "CA1005", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1006-A06", "store_id": "CA1006", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1007-A02", "store_id": "CA1007", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1007-A12", "store_id": "CA1007", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1009-A00", "store_id": "CA1009", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1010-A02", "store_id": "CA1010", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1011-A04", "store_id": "CA1011", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1012-A06", "store_id": "CA1012", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1014-A02", "store_id": "CA1014", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1016-A00", "store_id": "CA1016", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1017-A04", "store_id": "CA1017", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "CA1018-A04", "store_id": "CA1018", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}

=== data/trucks.jsonl (20 sample rows) ===
{"truck_id": "DC_CENTRAL-T0", "dc_id": "DC_CENTRAL", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_CENTRAL-T1", "dc_id": "DC_CENTRAL", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_CENTRAL-T2", "dc_id": "DC_CENTRAL", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_CENTRAL-T3", "dc_id": "DC_CENTRAL", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_CENTRAL-T4", "dc_id": "DC_CENTRAL", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_CENTRAL-T5", "dc_id": "DC_CENTRAL", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_NORTH-T0", "dc_id": "DC_NORTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_NORTH-T1", "dc_id": "DC_NORTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_NORTH-T2", "dc_id": "DC_NORTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_NORTH-T3", "dc_id": "DC_NORTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_NORTH-T4", "dc_id": "DC_NORTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_NORTH-T5", "dc_id": "DC_NORTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_SOUTH-T0", "dc_id": "DC_SOUTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_SOUTH-T1", "dc_id": "DC_SOUTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_SOUTH-T2", "dc_id": "DC_SOUTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_SOUTH-T3", "dc_id": "DC_SOUTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_SOUTH-T4", "dc_id": "DC_SOUTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}
{"truck_id": "DC_SOUTH-T5", "dc_id": "DC_SOUTH", "cube_ft3": 3400.0, "weight_lb": 40000.0, "depart": "2026-12-31T08:00:00-08:00"}

=== data/dc_stock.jsonl (20 sample rows) ===
{"dc_id": "DC_CENTRAL", "sku_id": "SKU00013", "cases": 6}
{"dc_id": "DC_CENTRAL", "sku_id": "SKU00034", "cases": 4}
{"dc_id": "DC_CENTRAL", "sku_id": "SKU00055", "cases": 3}
{"dc_id": "DC_CENTRAL", "sku_id": "SKU00083", "cases": 2}
{"dc_id": "DC_CENTRAL", "sku_id": "SKU00114", "cases": 5}
{"dc_id": "DC_CENTRAL", "sku_id": "SKU00150", "cases": 3}
{"dc_id": "DC_CENTRAL", "sku_id": "SKU00165", "cases": 5}
{"dc_id": "DC_NORTH", "sku_id": "SKU00014", "cases": 9}
{"dc_id": "DC_NORTH", "sku_id": "SKU00035", "cases": 6}
{"dc_id": "DC_NORTH", "sku_id": "SKU00056", "cases": 4}
{"dc_id": "DC_NORTH", "sku_id": "SKU00092", "cases": 1}
{"dc_id": "DC_NORTH", "sku_id": "SKU00128", "cases": 4}
{"dc_id": "DC_NORTH", "sku_id": "SKU00154", "cases": 6}
{"dc_id": "DC_NORTH", "sku_id": "SKU00178", "cases": 4}
{"dc_id": "DC_SOUTH", "sku_id": "SKU00033", "cases": 8}
{"dc_id": "DC_SOUTH", "sku_id": "SKU00054", "cases": 14}
{"dc_id": "DC_SOUTH", "sku_id": "SKU00073", "cases": 7}
{"dc_id": "DC_SOUTH", "sku_id": "SKU00112", "cases": 20}
{"dc_id": "DC_SOUTH", "sku_id": "SKU00147", "cases": 4}
{"dc_id": "DC_SOUTH", "sku_id": "SKU00163", "cases": 5}

=== data/notes.jsonl (20 sample rows) ===
{"note_id": "N0000", "store_id": "CA1000", "text": "Endcap 1 holds a vendor Halloween display; candy there is not on the planogram."}
{"note_id": "N0003", "store_id": "CA1001", "text": "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."}
{"note_id": "N0006", "store_id": "CA1002", "text": "Topstock above aisle 5 has overflow cases of baking decorations."}
{"note_id": "N0009", "store_id": "CA1003", "text": "Online pickup totes staged in backroom bay 3 may contain affected items."}
{"note_id": "N0012", "store_id": "CA1004", "text": "Aisle 9 moved to garden center during remodel; locations are not on planogram."}
{"note_id": "N0015", "store_id": "CA1005", "text": "Store-brand frosting labels are smudged from a printer fault; check ingredients by hand."}
{"note_id": "N0018", "store_id": "CA1006", "text": "Endcap 16 holds a vendor Halloween display; candy there is not on the planogram."}
{"note_id": "N0021", "store_id": "CA1007", "text": "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."}
{"note_id": "N0024", "store_id": "CA1008", "text": "Topstock above aisle 7 has overflow cases of baking decorations."}
{"note_id": "N0027", "store_id": "CA1009", "text": "Online pickup totes staged in backroom bay 4 may contain affected items."}
{"note_id": "N0030", "store_id": "CA1010", "text": "Aisle 9 moved to garden center during remodel; locations are not on planogram."}
{"note_id": "N0033", "store_id": "CA1011", "text": "Store-brand frosting labels are smudged from a printer fault; check ingredients by hand."}
{"note_id": "N0036", "store_id": "CA1012", "text": "Endcap 17 holds a vendor Halloween display; candy there is not on the planogram."}
{"note_id": "N0039", "store_id": "CA1013", "text": "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."}
{"note_id": "N0042", "store_id": "CA1014", "text": "Topstock above aisle 8 has overflow cases of baking decorations."}
{"note_id": "N0045", "store_id": "CA1015", "text": "Online pickup totes staged in backroom bay 15 may contain affected items."}
{"note_id": "N0048", "store_id": "CA1016", "text": "Aisle 5 moved to garden center during remodel; locations are not on planogram."}
{"note_id": "N0051", "store_id": "CA1017", "text": "Store-brand frosting labels are smudged from a printer fault; check ingredients by hand."}
{"note_id": "N0054", "store_id": "CA1018", "text": "Endcap 13 holds a vendor Halloween display; candy there is not on the planogram."}
{"note_id": "N0057", "store_id": "CA1019", "text": "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."}

=== data/substitutes.json (sample) ===
{"SKU00000": ["SKU00112"], "SKU00001": ["SKU00154"], "SKU00002": ["SKU00147"], "SKU00003": ["SKU00013", "SKU00165"], "SKU00004": ["SKU00014", "SKU00056"], "SKU00005": ["SKU00054", "SKU00112"], "SKU00006": ["SKU00112"], "SKU00007": ["SKU00073", "SKU00114"], "SKU00008": ["SKU00013"], "SKU00009": ["SKU00035", "SKU00056"], "SKU00010": ["SKU00112"], "SKU00011": ["SKU00034"], "SKU00021": ["SKU00054"], "SKU00022": ["SKU00083"], "SKU00023": ["SKU00154"], "SKU00024": ["SKU00112", "SKU00178"], "SKU00025": ["SKU00056"], "SKU00026": ["SKU00112"], "SKU00027": ["SKU00055"], "SKU00028": ["SKU00165"]}

OUTPUT PROTOCOL (follow exactly)
1. First emit the manifest between the lines <<<MANIFEST>>> and <<<END MANIFEST>>>.
   One JSON object per line: {"path": "...", "purpose": "...", "public": ["name(arg, arg) -> type", ...],
   "depends_on": ["path", ...]}
2. Then emit every manifest file, in manifest order, each as:
   <<<FILE path=relative/path.py>>>
   ...complete file contents...
   <<<END FILE>>>
3. Never emit text outside these blocks. No markdown fences inside files.
4. Every file is complete and runnable. Forbidden: pass as a body, TODO, NotImplementedError, "...",
   "rest omitted", placeholder comments.
5. Import shared types only from contract.py (already exists; do not re-emit it). Use its enums for every code value.
6. Every plan.jsonl record must include "src": the path of the module that emitted it.
7. Python 3.11, standard library plus pytest and duckdb only. Deterministic: no randomness without a fixed seed.
8. Unit tests for package X go in tests/unit/test_X_*.py immediately after package X.
9. Stop only after the last manifest file is complete.

