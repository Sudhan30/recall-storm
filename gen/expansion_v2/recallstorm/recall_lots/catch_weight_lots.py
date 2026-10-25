"""Random-weight meat/deli barcode parsing and grind log traceability."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class CatchWeightLotRecord:
    """Catch-weight meat/deli lot traceability record."""

    ref_id: str = "CW-LOT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class VariableWeightBarcodeParser:
    """Prefix-2 random-weight barcode parser."""

    ref_id: str = "CW-BAR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def extract_embedded_price_weight_upc(upc12: str) -> dict:
    """Extract item code and embedded price in dollars from a 12-digit Prefix-2 UPC."""
    _req(upc12, "upc12")
    digits = "".join(c for c in str(upc12) if c.isdigit())
    if len(digits) != 12 or not digits.startswith("2"):
        raise DataValidationError("Variable-weight UPC must be 12 digits starting with '2'")
    item_code = digits[1:6]
    price_usd = int(digits[7:11]) / 100.0
    return {"op": "extract_embedded_price_weight_upc", "item_code": item_code, "price_usd": price_usd, "src": "recallstorm/recall_lots/catch_weight_lots.py"}


def link_scale_plu_to_primal_lot(plu: str, primal_lot: str) -> dict:
    """Link an in-store scale PLU to its upstream primal/subprimal meat lot."""
    _req(plu, "plu")
    _req(primal_lot, "primal_lot")
    return {"op": "link_scale_plu_to_primal_lot", "plu": str(plu), "primal_lot": str(primal_lot), "src": "recallstorm/recall_lots/catch_weight_lots.py"}


def calculate_meat_chub_yield_loss(gross_lb: float, net_lb: float) -> float:
    """Calculate cutting/trim yield loss in pounds."""
    if gross_lb <= 0 or net_lb < 0 or net_lb > gross_lb:
        raise DataValidationError("Invalid gross/net weight")
    return round(float(gross_lb) - float(net_lb), 2)


def reconcile_case_weight_to_packages(case_lb: float, pkg_weights: list[float]) -> dict:
    """Reconcile master case catch-weight to individual retail tray weights."""
    if case_lb <= 0 or pkg_weights is None:
        raise DataValidationError("Invalid case_lb or pkg_weights")
    sum_pkg = round(sum(pkg_weights), 2)
    return {"op": "reconcile_case_weight_to_packages", "case_lb": case_lb, "pkg_lb": sum_pkg, "variance_lb": round(case_lb - sum_pkg, 2), "src": "recallstorm/recall_lots/catch_weight_lots.py"}


def trace_in_store_grind_logs(grind_batch_id: str, source_lots: list[str]) -> dict:
    """Trace FSIS-mandated in-store beef grind logs to source chub lots."""
    _req(grind_batch_id, "grind_batch_id")
    if not source_lots:
        raise DataValidationError("source_lots cannot be empty")
    return {"op": "trace_in_store_grind_logs", "grind_batch_id": str(grind_batch_id), "source_lots": sorted(source_lots), "src": "recallstorm/recall_lots/catch_weight_lots.py"}


def match_deli_slicing_batch_sheet(slicer_id: str, chub_lot: str) -> dict:
    """Match deli service-counter slicing logs to recalled deli meat chub lots."""
    _req(slicer_id, "slicer_id")
    _req(chub_lot, "chub_lot")
    return {"op": "match_deli_slicing_batch_sheet", "slicer_id": str(slicer_id), "chub_lot": str(chub_lot), "src": "recallstorm/recall_lots/catch_weight_lots.py"}


def flag_commingled_trim_batches(batches: list[dict], recalled_lot: str) -> list[str]:
    """Flag all store grind batches that commingled bench trim from recalled_lot."""
    _req(recalled_lot, "recalled_lot")
    if batches is None:
        raise DataValidationError("batches cannot be None")
    return [str(b["batch_id"]) for b in batches if recalled_lot in b.get("lots", [])]


def estimate_unweighed_case_count(total_lb: float, avg_case_lb: float = 40.0) -> int:
    """Estimate number of catch-weight cases from total pounds."""
    if total_lb < 0 or avg_case_lb <= 0:
        raise DataValidationError("Invalid weight inputs")
    return int(round(total_lb / avg_case_lb))


def validate_tare_weight_deductions(gross_lb: float, tare_lb: float) -> float:
    """Validate and subtract tray/wrap tare weight from gross weight."""
    if gross_lb <= 0 or tare_lb < 0 or tare_lb >= gross_lb:
        raise DataValidationError("Invalid gross/tare weights")
    return round(gross_lb - tare_lb, 3)


def generate_scale_purge_directive(store_id: str, plu_codes: list[str]) -> dict:
    """Generate a directive to purge recalled PLUs from meat/deli scales."""
    _req(store_id, "store_id")
    if not plu_codes:
        raise DataValidationError("plu_codes cannot be empty")
    return {"op": "generate_scale_purge_directive", "store_id": str(store_id), "plus": sorted(plu_codes), "src": "recallstorm/recall_lots/catch_weight_lots.py"}
