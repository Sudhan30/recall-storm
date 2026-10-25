"""Generate synthetic mock recall drills with ground-truth keys."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class SyntheticRecallScenario:
    """Synthetic mock recall drill scenario."""

    ref_id: str = "MOCK-SC-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class MockLotInjector:
    """Injector for seeding synthetic recalled and decoy lots into test environments."""

    ref_id: str = "MOCK-INJ-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def synthesize_class_i_listeria_notice(sku_id: str, lot_code: str = "L2601") -> dict:
    """Synthesize a mock Class I Listeria monocytogenes recall notice."""
    _req(sku_id, "sku_id")
    _req(lot_code, "lot_code")
    return {"op": "synthesize_class_i_listeria_notice", "sku_id": str(sku_id), "lot_code": str(lot_code), "class": "Class I", "src": "recallstorm/recall_lots/mock_recall_generator.py"}


def inject_seeded_lots_into_wms(dc_id: str, lots: list[str]) -> dict:
    """Seed mock recall lots into WMS test tables."""
    _req(dc_id, "dc_id")
    if not lots:
        raise DataValidationError("lots cannot be empty")
    return {"op": "inject_seeded_lots_into_wms", "dc_id": str(dc_id), "count": len(lots), "src": "recallstorm/recall_lots/mock_recall_generator.py"}


def generate_realistic_lot_typos(lot_code: str) -> list[str]:
    """Generate realistic OCR/human typos of lot_code for drill testing."""
    _req(lot_code, "lot_code")
    s = str(lot_code).upper()
    return [s, s.replace("0", "O"), s.replace("1", "I")]


def create_multi_dc_split_scenario(dcs: list[str], cases_per_dc: int = 10) -> dict:
    """Create a multi-DC split stock scenario."""
    if not dcs or cases_per_dc <= 0:
        raise DataValidationError("Invalid dcs or cases_per_dc")
    return {"op": "create_multi_dc_split_scenario", "dcs": sorted(dcs), "total_cases": len(dcs) * cases_per_dc, "src": "recallstorm/recall_lots/mock_recall_generator.py"}


def configure_blind_drill_parameters(drill_id: str, duration_hours: int = 4) -> dict:
    """Configure an unannounced blind mock recall drill."""
    _req(drill_id, "drill_id")
    if duration_hours <= 0:
        raise DataValidationError("duration_hours must be positive")
    return {"op": "configure_blind_drill_parameters", "drill_id": str(drill_id), "duration_hours": int(duration_hours), "src": "recallstorm/recall_lots/mock_recall_generator.py"}


def plant_decoy_unaffected_lots(target_lot: str) -> list[str]:
    """Generate decoy unaffected lot codes adjacent to target_lot."""
    _req(target_lot, "target_lot")
    return [f"{target_lot}_SAFE1", f"{target_lot}_SAFE2"]


def scale_scenario_store_count(base_stores: list[str], factor: int = 2) -> list[str]:
    """Scale a list of store IDs by factor for load testing."""
    if base_stores is None or factor <= 0:
        raise DataValidationError("Invalid base_stores or factor")
    return [f"{s}_{i}" for i in range(factor) for s in base_stores]


def generate_mock_press_release_pdf(drill_id: str, title: str = "MOCK RECALL DRILL") -> dict:
    """Generate a watermarked mock recall press release metadata record."""
    _req(drill_id, "drill_id")
    return {"op": "generate_mock_press_release_pdf", "drill_id": str(drill_id), "watermark": "EXERCISE ONLY", "title": title, "src": "recallstorm/recall_lots/mock_recall_generator.py"}


def build_expected_ground_truth_key(pulled_skus: list[str], kept_skus: list[str]) -> dict:
    """Build the expected ground-truth answer key for scoring a mock drill."""
    if pulled_skus is None or kept_skus is None:
        raise DataValidationError("Inputs cannot be None")
    return {"PULL": sorted(pulled_skus), "KEEP": sorted(kept_skus)}


def validate_scenario_solvability(tasks_mins: float, available_labor_mins: float) -> dict:
    """Verify that the mock recall scenario is solvable within available associate labor minutes."""
    if tasks_mins < 0 or available_labor_mins <= 0:
        raise DataValidationError("Invalid labor minute parameters")
    return {"op": "validate_scenario_solvability", "solvable": tasks_mins <= available_labor_mins, "src": "recallstorm/recall_lots/mock_recall_generator.py"}
