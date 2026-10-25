You are writing ONE package of Recall Storm, a retailer compliance drill system: recallstorm/route/.
Scenario: California AB 418 bans selling food containing FD&C Red No. 3 from 2027-01-01 00:00 local.
Pulled cases go back from stores to their distribution center (DC) on return trucks.

Write only:
- recallstorm/__init__.py (empty docstring module)
- recallstorm/route/  pack_returns(pulled_cases, skus, trucks, stores) exactly as in contract.py.
                      pulled_cases maps (store_id, sku_id) -> cases. Each store's cases ride trucks of its
                      own DC (Store.dc_id). Cube and weight per case come from Sku.case_cube_ft3 and
                      Sku.case_weight_lb. Every manifest stays within its truck's cube_ft3 and weight_lb;
                      every pulled case is on exactly one stop; a store's load may be split across trucks
                      when it does not fit on one; no empty manifests; each truck used at most once.
                      Deterministic. Raise a clear error if a DC lacks capacity for its returns.
- tests/unit/test_route_*.py
Write nothing else. No other package exists.

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
{"sku_id": "FDC1034191", "gtin": "07502264930572", "name": "Rainbow Sprinkles", "brand": "Chocolatera De Nayarit, S.A. De C.V.", "category": "baking decorations & dessert toppings", "ingredients": "SUGAR, CORN SYRUP, HYDROGENATED PALM KERNEL OIL, SOY LECITHIN, FD&C BLUE #1, FD&C YELLOW #5, FD&C YELLOW #6, FD&C RED #3, FD&C RED #40, SALT, HBT (BUTYLHYDROXYTOLUENE), CARNAUBA WAX.", "is_food": true, "is_ingested_drug": false, "case_units": 6, "case_cube_ft3": 2.05, "case_weight_lb": 23.2, "_real": true, "_src": "fdc:1034191"}
{"sku_id": "FDC1878485", "gtin": "00073621007017", "name": "Candy", "brand": "Angry Birds", "category": "candy", "ingredients": "SUGAR, CORN SYRUP, ADIPIC ACID, HYDROG. PALM KERNEL & PALM OILS AND SOYBEAN OIL MONO & DIGLYCERIDES, NATURAL & ARTIFICIAL FLAVORS, ARTIFICIAL COLORS FD&C RED 3, YELLOW 5, YELLOW 6, BLUE 2.", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.51, "case_weight_lb": 6.3, "_real": true, "_src": "fdc:1878485"}
{"sku_id": "FDC1913788", "gtin": "00811033712026", "name": "Maraschino Cherries Without Stem", "brand": "Bell Foods International", "category": "baking decorations & dessert toppings", "ingredients": "CHERRIES, HIGH FRUCTOSE CORN SYRUP, WATER, POTASSIUM SORBATE (A PRESERVATIVE), SODIUM BENZOATE (A PRESERVATIVE), CITRIC ACID, NATURAL AND ARTIFICIAL FLAVOR, FD&C RED #40, SULFUR DIOXIDE (A PRESERVATIVE).", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.43, "case_weight_lb": 4.6, "_real": true, "_src": "fdc:1913788"}
{"sku_id": "FDC1983505", "gtin": "00070572244003", "name": "Syrup, Bacon", "brand": "Tropical", "category": "syrups & molasses", "ingredients": "CORN SYRUP, HIGH FRUCTOSE CORN SYRUP, WATER, NATURAL AND ARTIFICIAL FLAVOR, SALT, POTASSIUM SORBATE (A PRESERVATIVE) AND CARAMEL COLOR.", "is_food": true, "is_ingested_drug": false, "case_units": 24, "case_cube_ft3": 1.51, "case_weight_lb": 5.1, "_real": true, "_src": "fdc:1983505"}
{"sku_id": "FDC2032505", "gtin": "00077290773105", "name": "Candy", "brand": "Bit-O-Honey", "category": "candy", "ingredients": "CORN SYRUP, SUGAR, NONFAT MILK, HYDROGENATED COCONUT OIL, ALMONDS, AND LESS THAN 2% OF HONEY, SALT, EGG WHITES, CANOLA AND/OR SAFFLOWER AND/OR PALM OIL, MODIFIED SOY PROTEIN, NATURAL FLAVOR, TBHQ AND CITRIC ACID (TO PRESERVE FRESHNESS).", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 2.12, "case_weight_lb": 5.2, "_real": true, "_src": "fdc:2032505"}
{"sku_id": "FDC2072562", "gtin": "00096619783953", "name": "Animal Crackers", "brand": "Kirkland Signature", "category": "cookies & biscuits", "ingredients": "ORGANIC WHEAT FLOUR, ORGANIC CANE SUGAR, ORGANIC PALM OIL, ORGANIC CANE INVERT SYRUP, ORGANIC DEGERMED CORN FLOUR, ORGANIC SUNFLOWER OIL, BAKING SODA, ORGANIC VANILLA EXTRACT, SALT, SOY LECITHIN, CREAM OF TARTAR, NATURAL FLAVOR, ORGANIC SPICE.", "is_food": true, "is_ingested_drug": false, "case_units": 8, "case_cube_ft3": 1.21, "case_weight_lb": 14.0, "_real": true, "_src": "fdc:2072562"}
{"sku_id": "FDC2099147", "gtin": "00007078446200", "name": "Graham Cracker", "brand": "Tops", "category": "crusts & dough", "ingredients": "GRAHAM CRACKER MEAL (ENRICHED FLOUR [WHEAT FLOUR, NIACIN, REDUCED IRON, THIAMIN MONONITRATE, RIBOFLAVIN, FOLIC ACID], SUGAR, WHOLE WHEAT FLOUR, PALM OIL, HIGH FRUCTOSE CORN SYRUP BROWN SUGAR, HONEY, SODIUM BICARBONATE, MOLASSES, SALT, MALT SYRUP [MALTED BARLEY, CORN], ARTIFICIAL FLAVOR), VEGETABLE SHORTENING (CONTAINS HYDROGENATED PALM KERNEL, PALM OIL, CANOLA OIL), SUGAR, CORNSTARCH.", "is_food": true, "is_ingested_drug": false, "case_units": 36, "case_cube_ft3": 0.82, "case_weight_lb": 6.8, "_real": true, "_src": "fdc:2099147"}
{"sku_id": "FDC2133371", "gtin": "00741643048683", "name": "Butter Syrup", "brand": "Lowes Foods", "category": "syrups & molasses", "ingredients": "CORN SYRUP, HIGH FRUCTOSE CORN SYRUP, WATER, SUGAR, NATURAL AND ARTIFICIAL FLAVOR, SALT, CARAMEL COLOR, POTASSIUM SORBATE (PRESERVATIVE), CELLULOSE GUM, SODIUM HEXAMETAPHOSPHATE.", "is_food": true, "is_ingested_drug": false, "case_units": 24, "case_cube_ft3": 1.09, "case_weight_lb": 6.4, "_real": true, "_src": "fdc:2133371"}
{"sku_id": "FDC2195999", "gtin": "00073621012912", "name": "Candy", "brand": "Pez", "category": "candy", "ingredients": "SUGAR, CORN SYRUP, ADIPIC ACID, HYDROGENATED PALM KERNEL & PALM OILS, MONO & DIGLYCERIDES, NATURAL & ARTIFICIAL FLAVORS.", "is_food": true, "is_ingested_drug": false, "case_units": 36, "case_cube_ft3": 1.02, "case_weight_lb": 5.0, "_real": true, "_src": "fdc:2195999"}
{"sku_id": "FDC2308934", "gtin": "00021333071390", "name": "Gummi Bears Candies, Gummi Bears", "brand": "Fareway", "category": "candy", "ingredients": "CORN SYRUP, SUGAR, WHITE GRAPE JUICE FROM CONCENTRATE, GELATIN, CITRIC ACID, SORBITOL, NATURAL AND ARTIFICIAL FLAVORS, CARNAUBA WAX, ARTIFICIAL COLORS (RED 40, YELLOW 5, YELLOW 6, BLUE 1).", "is_food": true, "is_ingested_drug": false, "case_units": 36, "case_cube_ft3": 1.75, "case_weight_lb": 21.2, "_real": true, "_src": "fdc:2308934"}
{"sku_id": "FDC2429227", "gtin": "00007789046152", "name": "Fruit Cocktail In 100% Juice, Fruit Cocktail", "brand": "Wegmans", "category": "canned fruit", "ingredients": "DICED PEACHES, DICED PEARS, WATER, GRAPES, PEACH PULP AND JUICE, PINEAPPLE SECTORS, PEAR JUICE CONCENTRATE, HALVED CHERRIES (COLORED RED WITH CARMINE), ASCORBIC ACID (VITAMIN C) TO PROTECT COLOR.", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.87, "case_weight_lb": 3.2, "_real": true, "_src": "fdc:2429227"}
{"sku_id": "FDC2493510", "gtin": "00011822446921", "name": "3 Pepper Jalapeno Beef Jerky, 3 Pepper Jalapeno", "brand": "Big Win", "category": "other snacks", "ingredients": "BEEF, SUGAR, WATER, SEA SALT, GARLIC POWDER, YEAST EXTRACT, NATURAL FLAVORS (JALAPENO, BLACK PEPPER, RED PEPPER), ONION POWDER, SPICES (OREGANO), CITRIC ACID, ROSEMARY EXTRACT WITH GREEN TEA EXTRACT, CELERY POWDER.", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.18, "case_weight_lb": 5.6, "_real": true, "_src": "fdc:2493510"}
{"sku_id": "FDC2524922", "gtin": "00078742374871", "name": "Sprinkle Mix", "brand": "Great Value", "category": "baking decorations & dessert toppings", "ingredients": "DEXTROSE, SUGAR, CORN STARCH, DEXTRIN, GLUCOSE SYRUP MAGNESIUM STEARATE, ARTIFICIAL VANILLA FAVOR, CONFECTIONER'S GLAZE, GUM ARABIC, CARNAUBA WAX, RED 40, RED 3, BLUE 1, YELLOW 5, YELLOW 6, BLUE2.", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 0.56, "case_weight_lb": 18.7, "_real": true, "_src": "fdc:2524922"}
{"sku_id": "FDC2567743", "gtin": "00070506072412", "name": "Rainbow Sprinkles", "brand": "Spice Farms", "category": "baking decorations & dessert toppings", "ingredients": "SUGAR, CORN STARCH, PALM OIL & PALM KERNEL OIL, DEXTRIN, SOY LECITHIN, SUNFLOWER LECITHIN, CARNAUBA WAX, CONFECTIONER'S GLAZE, FD&C YELLOW #5 LAKE, FD&C YELLOW #6 LAKE, FD&C BLUE #1 LAKE, FD&C RED #40 LAKE, FD&C RED #3, FD&C BLUE #2, FD&C RED #40, FD&C BLUE #1", "is_food": true, "is_ingested_drug": false, "case_units": 36, "case_cube_ft3": 1.22, "case_weight_lb": 7.9, "_real": true, "_src": "fdc:2567743"}
{"sku_id": "FDC2612060", "gtin": "00049646006823", "name": "Candied Jalapenos, Candied", "brand": "Preserved Harvest", "category": "pickles, olives, peppers & relishes", "ingredients": "JALAPENOS, (SALT, VINEGAR & CALCIUM CHLORIDE) SUGAR, WATER, VINEGAR, SALT, SPICES.", "is_food": true, "is_ingested_drug": false, "case_units": 24, "case_cube_ft3": 1.13, "case_weight_lb": 19.9, "_real": true, "_src": "fdc:2612060"}
{"sku_id": "FDC2655277", "gtin": "00079200079291", "name": "Gummy Clusters Candy, Gummy Clusters", "brand": "Nerds", "category": "candy", "ingredients": "CORN SYRUP, SUGAR, DEXTROSE, GELATIN, MODIFIED CORN STARCH, WATER, CONTAINS 2% OR LESS OF MALIC ACID (DL-MALIC ACID), CITRIC ACID, SODIUM CITRATE, APPLE JUICE CONCENTRATE, NATURAL AND ARTIFICIAL FLAVORS, GUM ARABIC, CARNAUBA WAX, RED 40 LAKE, RED 40, COLOR ADDED.", "is_food": true, "is_ingested_drug": false, "case_units": 36, "case_cube_ft3": 1.66, "case_weight_lb": 11.4, "_real": true, "_src": "fdc:2655277"}
{"sku_id": "FDC2677948", "gtin": "00085239015223", "name": "Mini Brownies With Frosting, Frosting", "brand": "Market Pantry", "category": "cakes, cupcakes, snack cakes", "ingredients": "BROWNIE: SUGAR, ENRICHED WHEAT FLOUR (WHEAT FLOUR, NIACIN, REDUCED IRON, THIAMINE MONONITRATE, RIBOFLAVIN, FOLIC ACID), SOYBEAN OIL, EGG WHITE, CORN SYRUP, WATER, SHORTENING (PALM, CANOLA, AND MODIFIED PALM OIL), CHOCOLATE (SUGAR, CHOCOLATE LIQUOR, COCOA BUTTER, SOY LECITHIN, VANILLA EXTRACT), COCOA POWDER (PROCESSED WITH ALKALI), SALT, NATURAL AND ARTIFICIAL FLAVOR, WHEY POWDER, MODIFIED CORN STARCH, LEAVENING (SODIUM ACID PYROPHOSPHATE, SODIUM BICARBONATE, CORN STARCH, MONOCALCIUM PHOSPHATE, CALCIUM SULFATE), SOY LECITHIN. ICING: ICING SUGAR, SHORTENING (CANOLA, PALM, MODIFIED PALM AND PALM KERNEL OIL), INVERT SUGAR, MARGARINE [SOYBEAN AND MODIFIED PALM OIL, WATER, SALT, WHEY POWDER, SOY LECITHIN, MONOGLYCERIDES, NATURAL FLAVOR, VITAMIN A PALMITATE, VITAMIN D3, COLOR (ANNATTO)], GLUCOSE, WATER, MODIFIED CORN STARCH, SKIM MILK POWDER, MONO AND DIGLYCERIDES, YELLOW 5, BLUE 1), ARTIFICIAL FLAVOR, SALT, POLYSORBATE 60. SPRINKLES: SUGAR, MODIFIED CORN STARCH, PALM KERNEL OIL, CORN STARCH, GUM ARABIC, SOY LECITHIN, ARTIFICIAL FLAVOR, POLYSORBATE 60.", "is_food": true, "is_ingested_drug": false, "case_units": 36, "case_cube_ft3": 0.82, "case_weight_lb": 15.7, "_real": true, "_src": "fdc:2677948"}
{"sku_id": "VAR0021", "gtin": "02000000000213", "name": "Dipped & Sprinkled Pretzels, Dipped & Sprinkled", "brand": "Favorite Day", "category": "popcorn, peanuts, seeds & related snacks", "ingredients": "CONFECTIONERY COATING (SUGAR, PALM KERNEL OIL, NONFAT DRY MILK, LACTOSE, TITANIUM DIOXIDE [COLOR], SOY LECITHIN [AN EMULSIFIER], DISTILLED MONOGLYCERIDES, VANILLA, FRACTIONATED COCONUT OIL, BLUE 1 LAKE, RED 40 LAKE), PRETZELS (ENRICHED WHEAT FLOUR [WHEAT FLOUR, NIACIN, REDUCED IRON, THIAMINE MONONITRATE, RIBOFLAVIN, FOLIC ACID], CORN SYRUP, SALT, VEGETABLE OIL [MAY CONTAIN ONE OR MORE OF THE FOLLOWING: CANOLA, CORN, SOYBEAN], VITAL WHEAT GLUTEN, SODIUM BICARBONATE, YEAST), NONPAREILS (SUGAR, CORNSTARCH, E127, RED 40, CARNAUBA WAX, CONFECTIONER'S GLAZE, BLUE 1).", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.81, "case_weight_lb": 4.2, "_real": false, "_kind": "alias:E127", "_base": "FDC2605087"}
{"sku_id": "VAR0081", "gtin": "02000000000817", "name": "Fruit Cocktail In Heavy Syrup", "brand": "Island Sun", "category": "canned fruit", "ingredients": "DICED PEACHES, DICED PEARS, GRAPES, PINEAPPLE SEGMENTS, CHERRIES (Red Dye 3), WATER, SUGAR, CITRIC ACID.", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 1.85, "case_weight_lb": 8.9, "_real": false, "_kind": "alias:Red Dye 3", "_base": "FDC2066569"}
{"sku_id": "VAR0141", "gtin": "02000000001418", "name": "Easter Basket Candy Pack #7", "brand": "The Candy Shoppe", "category": "seasonal kits", "ingredients": "KIT CONTAINS: Frosted Heart Pretzels, Frosted Heart: WHITE CONFECTIONERY COATING (SUGAR, PALM KERNEL OIL, NONFAT MILK POWDER, LACTOSE, TITANIUM DIOXIDE [COLOR], SOY LECITHIN (AN EMULSIFIERT, DISTILLED MONOGLYCERIDES, VANILLA), HEART SHAPED PRETZELS (ENRICHED WHEAT FLOUR (WHEAT FLOUR, NIACIN, REDUCED IRON, THIAMINE MONONITRATE, RIBOFLAVIN, FOLIC ACID), SALT, VEGETABLE OIL (MAY CONTAIN ONE OR MORE OF THE FOLLOWING: CANOLA, CORN, SOYBEAN], CORN SYRUP, SODIUM BICARBONATE, YEAST), PINK, LIGHT PINK, RED NONPAREILS (SUGAR, CORNSTARCH, RED 3 POWDER, RED 40 POWDER, CONFECTIONER'S GLAZE, CARNAUBA WAX). | Maraschino Cherries With Stems, Maraschino: CHERRIES, WATER, CORN SYRUP, HIGH FRUCTOSE CORN SYRUP, CITRIC ACID, NATURAL AND ARTIFICIAL FLAVOR, POTASSIUM SORBATE AND SODIUM BENZOATE (PRESERVATIVES), RED 40, SULFUR DIOXIDE (PRESERVATIVE).", "is_food": true, "is_ingested_drug": false, "case_units": 12, "case_cube_ft3": 2.03, "case_weight_lb": 4.9, "_real": false, "_kind": "bundle_kit", "_base": "FDC2504071"}

=== data/stores.jsonl (20 sample rows) ===
{"store_id": "SAMS4735", "format": "SAMS", "state": "CA", "city": "La Habra", "lat": 33.91287, "lon": -117.97008, "district": "D09", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/563170433", "_name": "Sam's Club", "_addr": "1400 South Beach Boulevard"}
{"store_id": "SAMS4767", "format": "SAMS", "state": "CA", "city": "Palmdale", "lat": 34.60838, "lon": -118.14441, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/472905677", "_name": "Sam's Club", "_addr": "39940 10th Street West"}
{"store_id": "SAMS6405", "format": "SAMS", "state": "CA", "city": "Yuba City", "lat": 39.13926, "lon": -121.64549, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:node/11993193507", "_name": "Sam's Club", "_addr": "900 North Walton Avenue"}
{"store_id": "SAMS6621", "format": "SAMS", "state": "CA", "city": "Roseville", "lat": 38.78642, "lon": -121.28773, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/45368716", "_name": "Sam's Club", "_addr": "904 Pleasant Grove Boulevard"}
{"store_id": "WM1563", "format": "SUPERCENTER", "state": "CA", "city": "Lancaster", "lat": 34.6938, "lon": -118.17406, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:relation/6955798", "_name": "Walmart Supercenter", "_addr": "44665 Valley Central Way"}
{"store_id": "WM1574", "format": "SUPERCENTER", "state": "CA", "city": "Bakersfield", "lat": 35.29875, "lon": -119.02938, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/59822569", "_name": "Walmart Supercenter", "_addr": "6225 Colony Street"}
{"store_id": "WM1575", "format": "SUPERCENTER", "state": "CA", "city": "Oroville", "lat": 39.49063, "lon": -121.57145, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/474456102", "_name": "Walmart Supercenter", "_addr": "465 Cal Oak Road"}
{"store_id": "WM1588", "format": "SUPERCENTER", "state": "CA", "city": "Victorville", "lat": 34.46512, "lon": -117.35443, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/1008760751", "_name": "Walmart Supercenter", "_addr": "11896 Amargosa Road"}
{"store_id": "WM1608", "format": "SUPERCENTER", "state": "CA", "city": "Red Bluff", "lat": 40.16293, "lon": -122.23437, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/546732624", "_name": "Walmart Supercenter", "_addr": "608 Luther Road"}
{"store_id": "WM1616", "format": "DISCOUNT", "state": "CA", "city": "Susanville", "lat": 40.40892, "lon": -120.63758, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/436352557", "_name": "Walmart", "_addr": "2900 Main Street"}
{"store_id": "WM1630", "format": "SUPERCENTER", "state": "CA", "city": "Yreka", "lat": 41.69865, "lon": -122.64457, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/360427744", "_name": "Walmart Supercenter", "_addr": "1906 Fort Jones Road"}
{"store_id": "WM1899", "format": "SUPERCENTER", "state": "CA", "city": "Riverside", "lat": 33.93853, "lon": -117.28613, "district": "D09", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/444490322", "_name": "Walmart Supercenter", "_addr": "6250 Valley Springs Parkway"}
{"store_id": "WM1912", "format": "SUPERCENTER", "state": "CA", "city": "Corona", "lat": 33.89079, "lon": -117.51729, "district": "D09", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/201454867", "_name": "Walmart Supercenter", "_addr": "479 North McKinley Street"}
{"store_id": "WM2028", "format": "SUPERCENTER", "state": "CA", "city": "Riverside", "lat": 33.93712, "lon": -117.45539, "district": "D09", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:node/928693137", "_name": "Walmart Supercenter", "_addr": "5200 Van Buren Boulevard"}
{"store_id": "WM2333", "format": "DISCOUNT", "state": "CA", "city": "Apple Valley", "lat": 34.52554, "lon": -117.22309, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/460848367", "_name": "Walmart", "_addr": "20251 Happy Trails Highway"}
{"store_id": "WM2523", "format": "DISCOUNT", "state": "CA", "city": "Brea", "lat": 33.91346, "lon": -117.86523, "district": "D09", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/142606474", "_name": "Walmart", "_addr": "2595 East Imperial Highway"}
{"store_id": "WM3139", "format": "NEIGHBORHOOD", "state": "CA", "city": "Bakersfield", "lat": 35.37013, "lon": -119.14746, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:node/5315598907", "_name": "Walmart Neighborhood Market", "_addr": "1249 Allen Road"}
{"store_id": "WM3141", "format": "NEIGHBORHOOD", "state": "CA", "city": "Bakersfield", "lat": 35.35339, "lon": -118.94765, "district": "D06", "dc_id": "DC_CENTRAL", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:node/4093403024", "_name": "Walmart Neighborhood Market", "_addr": "5037 East Brundage Lane"}
{"store_id": "WM4127", "format": "NEIGHBORHOOD", "state": "CA", "city": "Woodland", "lat": 38.68087, "lon": -121.78792, "district": "D01", "dc_id": "DC_NORTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:node/5315598128", "_name": "Walmart Neighborhood Market", "_addr": "215 California Street"}
{"store_id": "WM5603", "format": "NEIGHBORHOOD", "state": "CA", "city": "Downey", "lat": 33.92814, "lon": -118.14774, "district": "D09", "dc_id": "DC_SOUTH", "tz": "America/Los_Angeles", "_real": true, "_src": "osm:way/351803045", "_name": "Walmart Neighborhood Market", "_addr": "12270 Paramount Boulevard"}

=== data/facings.jsonl (20 sample rows) ===
{"store_id": "SAMS4735", "sku_id": "FDC1034191", "loc": {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 1}, "units": 11}
{"store_id": "SAMS6405", "sku_id": "FDC1458937", "loc": {"aisle": "A01", "bay": 1, "shelf": 1, "pos": 3}, "units": 10}
{"store_id": "WM1563", "sku_id": "FDC1460285", "loc": {"aisle": "A01", "bay": 1, "shelf": 4, "pos": 3}, "units": 7}
{"store_id": "WM1563", "sku_id": "FDC2651690", "loc": {"aisle": "A06", "bay": 5, "shelf": 4, "pos": 2}, "units": 9}
{"store_id": "WM1574", "sku_id": "FDC2314254", "loc": {"aisle": "A04", "bay": 4, "shelf": 2, "pos": 1}, "units": 32}
{"store_id": "WM1575", "sku_id": "FDC2016322", "loc": {"aisle": "A02", "bay": 2, "shelf": 4, "pos": 6}, "units": 35}
{"store_id": "WM1575", "sku_id": "VAR0073", "loc": {"aisle": "A08", "bay": 1, "shelf": 4, "pos": 5}, "units": 16}
{"store_id": "WM1588", "sku_id": "FDC2535728", "loc": {"aisle": "A05", "bay": 5, "shelf": 2, "pos": 4}, "units": 7}
{"store_id": "WM1608", "sku_id": "FDC2110231", "loc": {"aisle": "A03", "bay": 3, "shelf": 5, "pos": 3}, "units": 17}
{"store_id": "WM1616", "sku_id": "FDC1893879", "loc": {"aisle": "A01", "bay": 2, "shelf": 3, "pos": 2}, "units": 33}
{"store_id": "WM1630", "sku_id": "FDC2066567", "loc": {"aisle": "A02", "bay": 5, "shelf": 4, "pos": 4}, "units": 20}
{"store_id": "WM1630", "sku_id": "VAR0161", "loc": {"aisle": "A08", "bay": 4, "shelf": 4, "pos": 3}, "units": 8}
{"store_id": "WM1899", "sku_id": "FDC2606004", "loc": {"aisle": "A06", "bay": 3, "shelf": 2, "pos": 2}, "units": 8}
{"store_id": "WM1912", "sku_id": "FDC2172550", "loc": {"aisle": "A04", "bay": 1, "shelf": 5, "pos": 1}, "units": 30}
{"store_id": "WM2028", "sku_id": "FDC1924887", "loc": {"aisle": "A01", "bay": 5, "shelf": 2, "pos": 6}, "units": 32}
{"store_id": "WM2028", "sku_id": "VAR0001", "loc": {"aisle": "A07", "bay": 4, "shelf": 2, "pos": 5}, "units": 21}
{"store_id": "WM2523", "sku_id": "FDC2009631", "loc": {"aisle": "A01", "bay": 4, "shelf": 1, "pos": 1}, "units": 23}
{"store_id": "WM3139", "sku_id": "FDC2415607", "loc": {"aisle": "A03", "bay": 2, "shelf": 5, "pos": 2}, "units": 10}
{"store_id": "WM3141", "sku_id": "FDC2578244", "loc": {"aisle": "A04", "bay": 2, "shelf": 2, "pos": 5}, "units": 9}
{"store_id": "WM4127", "sku_id": "FDC2752913", "loc": {"aisle": "A05", "bay": 1, "shelf": 3, "pos": 6}, "units": 29}

=== data/associates.jsonl (20 sample rows) ===
{"associate_id": "SAMS4735-A00", "store_id": "SAMS4735", "district": "D09", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "SAMS4767-A01", "store_id": "SAMS4767", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "SAMS6405-A02", "store_id": "SAMS6405", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "SAMS6621-A03", "store_id": "SAMS6621", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1563-A04", "store_id": "WM1563", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1574-A01", "store_id": "WM1574", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1574-A12", "store_id": "WM1574", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1575-A09", "store_id": "WM1575", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1588-A06", "store_id": "WM1588", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1608-A03", "store_id": "WM1608", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1616-A00", "store_id": "WM1616", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1630-A05", "store_id": "WM1630", "district": "D01", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1899-A02", "store_id": "WM1899", "district": "D09", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1899-A13", "store_id": "WM1899", "district": "D09", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM1912-A10", "store_id": "WM1912", "district": "D09", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM2028-A07", "store_id": "WM2028", "district": "D09", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM2333-A04", "store_id": "WM2333", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM3139-A03", "store_id": "WM3139", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM3141-A06", "store_id": "WM3141", "district": "D06", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}
{"associate_id": "WM5603-A01", "store_id": "WM5603", "district": "D09", "is_floater": false, "shift_start": "2026-12-30T22:00:00-08:00", "shift_end": "2026-12-31T06:00:00-08:00"}

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
{"dc_id": "DC_CENTRAL", "sku_id": "FDC1141715", "cases": 12}
{"dc_id": "DC_CENTRAL", "sku_id": "FDC2013052", "cases": 5}
{"dc_id": "DC_CENTRAL", "sku_id": "FDC2093122", "cases": 5}
{"dc_id": "DC_CENTRAL", "sku_id": "FDC2178255", "cases": 9}
{"dc_id": "DC_CENTRAL", "sku_id": "FDC2427753", "cases": 5}
{"dc_id": "DC_CENTRAL", "sku_id": "FDC2544428", "cases": 4}
{"dc_id": "DC_CENTRAL", "sku_id": "FDC2660333", "cases": 4}
{"dc_id": "DC_NORTH", "sku_id": "FDC1877171", "cases": 4}
{"dc_id": "DC_NORTH", "sku_id": "FDC2026573", "cases": 3}
{"dc_id": "DC_NORTH", "sku_id": "FDC2102896", "cases": 2}
{"dc_id": "DC_NORTH", "sku_id": "FDC2284520", "cases": 6}
{"dc_id": "DC_NORTH", "sku_id": "FDC2454962", "cases": 11}
{"dc_id": "DC_NORTH", "sku_id": "FDC2594947", "cases": 3}
{"dc_id": "DC_NORTH", "sku_id": "FDC421530", "cases": 3}
{"dc_id": "DC_SOUTH", "sku_id": "FDC1913788", "cases": 6}
{"dc_id": "DC_SOUTH", "sku_id": "FDC2051416", "cases": 7}
{"dc_id": "DC_SOUTH", "sku_id": "FDC2122309", "cases": 4}
{"dc_id": "DC_SOUTH", "sku_id": "FDC2338061", "cases": 2}
{"dc_id": "DC_SOUTH", "sku_id": "FDC2499832", "cases": 3}
{"dc_id": "DC_SOUTH", "sku_id": "FDC2612440", "cases": 3}

=== data/notes.jsonl (20 sample rows) ===
{"note_id": "N0000", "store_id": "SAMS4735", "text": "Endcap 16 holds a vendor Halloween display; candy there is not on the planogram."}
{"note_id": "N0003", "store_id": "SAMS4767", "text": "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."}
{"note_id": "N0006", "store_id": "SAMS6405", "text": "Topstock above aisle 12 has overflow cases of baking decorations."}
{"note_id": "N0009", "store_id": "SAMS6621", "text": "Online pickup totes staged in backroom bay 4 may contain affected items."}
{"note_id": "N0012", "store_id": "WM1563", "text": "Aisle 5 moved to garden center during remodel; locations are not on planogram."}
{"note_id": "N0015", "store_id": "WM1574", "text": "Store-brand frosting labels are smudged from a printer fault; check ingredients by hand."}
{"note_id": "N0018", "store_id": "WM1575", "text": "Endcap 14 holds a vendor Halloween display; candy there is not on the planogram."}
{"note_id": "N0021", "store_id": "WM1588", "text": "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."}
{"note_id": "N0024", "store_id": "WM1608", "text": "Topstock above aisle 2 has overflow cases of baking decorations."}
{"note_id": "N0027", "store_id": "WM1616", "text": "Online pickup totes staged in backroom bay 1 may contain affected items."}
{"note_id": "N0030", "store_id": "WM1630", "text": "Aisle 7 moved to garden center during remodel; locations are not on planogram."}
{"note_id": "N0033", "store_id": "WM1899", "text": "Store-brand frosting labels are smudged from a printer fault; check ingredients by hand."}
{"note_id": "N0036", "store_id": "WM1912", "text": "Endcap 20 holds a vendor Halloween display; candy there is not on the planogram."}
{"note_id": "N0039", "store_id": "WM2028", "text": "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."}
{"note_id": "N0042", "store_id": "WM2333", "text": "Topstock above aisle 6 has overflow cases of baking decorations."}
{"note_id": "N0045", "store_id": "WM2523", "text": "Online pickup totes staged in backroom bay 10 may contain affected items."}
{"note_id": "N0048", "store_id": "WM3139", "text": "Aisle 2 moved to garden center during remodel; locations are not on planogram."}
{"note_id": "N0051", "store_id": "WM3141", "text": "Store-brand frosting labels are smudged from a printer fault; check ingredients by hand."}
{"note_id": "N0054", "store_id": "WM4127", "text": "Endcap 2 holds a vendor Halloween display; candy there is not on the planogram."}
{"note_id": "N0057", "store_id": "WM5603", "text": "Frito-Lay DSD rep restocks Tuesdays; DSD items are vendor-pulled, do not pack for DC return."}

=== data/substitutes.json (sample) ===
{"FDC1034191": ["VAR0172"], "FDC1039055": ["FDC2009631", "FDC2030891"], "FDC1096385": ["FDC2594947", "VAR0182"], "FDC1138169": ["FDC2028308", "FDC2278504"], "FDC1152536": ["VAR0172"], "FDC1152555": ["FDC1863608"], "FDC1850898": ["FDC2101396", "VAR0182"], "FDC1851197": ["FDC2099158", "FDC2099175"], "FDC1861265": ["FDC1858097", "FDC2016691"], "FDC1863607": ["FDC2067256", "FDC2656035"], "FDC1864116": ["FDC1889618"], "FDC1873319": ["FDC2540675", "FDC2606211"], "FDC1874472": ["FDC2525111"], "FDC1878485": ["FDC2415865"], "FDC1878835": ["FDC2541940"], "FDC1885241": ["FDC2630123"], "FDC1885264": ["FDC2375329"], "FDC1885345": ["FDC2016691"], "FDC1885462": ["FDC1889890", "FDC2415607"], "FDC1886623": ["FDC2454957", "VAR0159"]}

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

