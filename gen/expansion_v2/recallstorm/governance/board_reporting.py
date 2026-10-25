"""Board Risk Committee packages and D&O fiduciary oversight briefs."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class RiskCommitteePackage:
    """Quarterly Board Audit & Risk Committee food-safety compliance package."""

    ref_id: str = "BRD-PCK-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class FiduciaryOversightBrief:
    """Caremark fiduciary oversight brief for the Board of Directors."""

    ref_id: str = "BRD-FID-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def compile_quarterly_enterprise_recall_summary(quarter: str, recalls_executed: int, avg_completion_pct: float) -> dict:
    """Compile quarterly enterprise recall summary for the Board."""
    _req(quarter, "quarter")
    if recalls_executed < 0 or not (0.0 <= avg_completion_pct <= 100.0):
        raise DataValidationError("Invalid recall count or avg_completion_pct")
    return {"op": "compile_quarterly_enterprise_recall_summary", "quarter": str(quarter), "recalls": int(recalls_executed), "avg_completion_pct": float(avg_completion_pct), "src": "recallstorm/governance/board_reporting.py"}


def quantify_unmitigated_state_ban_exposures(skus_remaining: int, avg_revenue_per_sku: float) -> float:
    """Quantify annual revenue at risk from un-reformulated SKUs subject to upcoming state additive bans."""
    if skus_remaining < 0 or avg_revenue_per_sku < 0:
        raise DataValidationError("Negative exposure inputs")
    return round(float(skus_remaining) * float(avg_revenue_per_sku), 2)


def report_material_fda_warning_letter_risks(open_483_observations: int) -> dict:
    """Report material FDA Form 483 / Warning Letter risks to the Risk Committee."""
    if open_483_observations < 0:
        raise DataValidationError("open_483_observations cannot be negative")
    return {"op": "report_material_fda_warning_letter_risks", "material_risk": open_483_observations > 0, "count": int(open_483_observations), "src": "recallstorm/governance/board_reporting.py"}


def summarize_whistleblower_and_audit_exceptions(tips: int, audit_gaps: int) -> dict:
    """Summarize ethics hotline tips and third-party audit exceptions for the Board."""
    if tips < 0 or audit_gaps < 0:
        raise DataValidationError("Negative counts")
    return {"op": "summarize_whistleblower_and_audit_exceptions", "tips": int(tips), "audit_gaps": int(audit_gaps), "src": "recallstorm/governance/board_reporting.py"}


def benchmark_compliance_maturity_against_peers(our_score: float, industry_median: float = 85.0) -> dict:
    """Benchmark enterprise recall maturity score against retail peer median."""
    if not (0.0 <= our_score <= 100.0) or not (0.0 <= industry_median <= 100.0):
        raise DataValidationError("Scores must be in [0, 100]")
    return {"op": "benchmark_compliance_maturity_against_peers", "outperforming": our_score >= industry_median, "spread": round(our_score - industry_median, 2), "src": "recallstorm/governance/board_reporting.py"}


def track_capex_investment_in_esl_and_epcis(esl_capex_musd: float, epcis_capex_musd: float) -> float:
    """Sum capital expenditure in Electronic Shelf Labels and GS1 EPCIS traceability."""
    if esl_capex_musd < 0 or epcis_capex_musd < 0:
        raise DataValidationError("Negative CapEx inputs")
    return round(float(esl_capex_musd) + float(epcis_capex_musd), 2)


def highlight_supply_chain_single_point_failures(single_sourced_skus: int) -> dict:
    """Highlight single-source co-packer dependencies in critical categories."""
    if single_sourced_skus < 0:
        raise DataValidationError("single_sourced_skus cannot be negative")
    return {"op": "highlight_supply_chain_single_point_failures", "count": int(single_sourced_skus), "action_required": single_sourced_skus > 0, "src": "recallstorm/governance/board_reporting.py"}


def document_crisis_simulation_readiness_scores(drills_run: int, pass_rate_pct: float) -> dict:
    """Document enterprise mock-recall simulation readiness scores."""
    if drills_run < 0 or not (0.0 <= pass_rate_pct <= 100.0):
        raise DataValidationError("Invalid drill metrics")
    return {"op": "document_crisis_simulation_readiness_scores", "drills_run": int(drills_run), "pass_rate_pct": float(pass_rate_pct), "src": "recallstorm/governance/board_reporting.py"}


def provide_directors_and_officers_liability_view(caremark_controls_active: bool = True) -> dict:
    """Document Caremark mission-critical food-safety reporting controls for D&O governance."""
    return {"op": "provide_directors_and_officers_liability_view", "caremark_compliant": bool(caremark_controls_active), "src": "recallstorm/governance/board_reporting.py"}


def archive_signed_board_resolution_minutes(resolution_id: str, quarter: str) -> dict:
    """Archive Corporate Secretary signed Board Risk Committee minutes."""
    _req(resolution_id, "resolution_id")
    _req(quarter, "quarter")
    return {"op": "archive_signed_board_resolution_minutes", "resolution_id": str(resolution_id), "quarter": str(quarter), "src": "recallstorm/governance/board_reporting.py"}
