"""Total Cost of Recall P&L aggregation and CFO financial bridges."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class RecallCostAggregator:
    """Aggregator for direct and indirect recall costs."""

    ref_id: str = "FIN-AGG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class TotalCostOfRecallModel:
    """Total Cost of Recall (TCOR) P&L impact model."""

    ref_id: str = "FIN-TCOR-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def sum_direct_product_write_off_at_cost(sku_costs: list[float]) -> float:
    """Sum direct merchandise cost of pulled inventory."""
    if sku_costs is None or any(c < 0 for c in sku_costs):
        raise DataValidationError("Invalid sku_costs")
    return round(sum(sku_costs), 2)


def calculate_store_and_dc_execution_labor_cost(store_hours: float, dc_hours: float, hourly_rate: float = 22.0) -> float:
    """Calculate combined store and DC associate execution labor cost."""
    if store_hours < 0 or dc_hours < 0 or hourly_rate <= 0:
        raise DataValidationError("Invalid labor hours or rate")
    return round((store_hours + dc_hours) * hourly_rate, 2)


def quantify_lost_margin_from_out_of_stocks(unreplaced_units: int, unit_margin_usd: float) -> float:
    """Quantify lost gross margin from empty facings not covered by substitute allocations."""
    if unreplaced_units < 0 or unit_margin_usd < 0:
        raise DataValidationError("Negative margin inputs")
    return round(unreplaced_units * unit_margin_usd, 2)


def add_reverse_freight_and_destruction_fees(freight_usd: float, destruction_usd: float) -> float:
    """Sum reverse logistics transportation and landfill/incineration fees."""
    if freight_usd < 0 or destruction_usd < 0:
        raise DataValidationError("Negative freight or destruction fees")
    return round(freight_usd + destruction_usd, 2)


def deduct_recovered_vendor_chargebacks_and_rma(gross_cost_usd: float, recovered_usd: float) -> float:
    """Deduct vendor RMA credits and execution chargebacks from gross recall cost."""
    if gross_cost_usd < 0 or recovered_usd < 0:
        raise DataValidationError("Negative cost or recovery")
    return round(max(0.0, gross_cost_usd - recovered_usd), 2)


def incorporate_regulatory_fines_and_legal_fees(fines_usd: float, legal_usd: float) -> float:
    """Sum statutory civil penalties and outside legal defense costs."""
    if fines_usd < 0 or legal_usd < 0:
        raise DataValidationError("Negative fines or legal fees")
    return round(fines_usd + legal_usd, 2)


def estimate_brand_equity_halo_basket_erosion(lost_trips: int, avg_basket_margin_usd: float = 18.0) -> float:
    """Estimate indirect basket erosion when a private-label recall reduces customer trips."""
    if lost_trips < 0 or avg_basket_margin_usd < 0:
        raise DataValidationError("Negative halo inputs")
    return round(lost_trips * avg_basket_margin_usd, 2)


def compute_net_unrecovered_recall_p_and_l_hit(gross_loss_usd: float, vendor_recovery_usd: float, insurance_recovery_usd: float = 0.0) -> float:
    """Compute net unrecovered P&L impact after vendor and insurance recoveries."""
    if gross_loss_usd < 0 or vendor_recovery_usd < 0 or insurance_recovery_usd < 0:
        raise DataValidationError("Negative P&L inputs")
    return round(max(0.0, gross_loss_usd - vendor_recovery_usd - insurance_recovery_usd), 2)


def attribute_cost_by_merchandising_buying_desk(desk_costs: dict[str, float]) -> dict[str, float]:
    """Return rounded recall costs attributed by merchandising buying desk."""
    if desk_costs is None or any(v < 0 for v in desk_costs.values()):
        raise DataValidationError("Invalid desk_costs")
    return {k: round(float(v), 2) for k, v in desk_costs.items()}


def generate_cfo_recall_financial_bridge(gross_usd: float, recovered_usd: float) -> dict:
    """Generate a CFO financial waterfall bridge from gross recall cost to net P&L impact."""
    net = deduct_recovered_vendor_chargebacks_and_rma(gross_usd, recovered_usd)
    return {"op": "generate_cfo_recall_financial_bridge", "gross_usd": round(gross_usd, 2), "recovered_usd": round(recovered_usd, 2), "net_usd": net, "src": "recallstorm/analytics/financial_impact.py"}
