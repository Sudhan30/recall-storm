"""Utah specialty electronic cigarette permit and flavor restrictions."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class UtElectronicCigaretteRule:
    """Domain entity for Utah Code 26B-7-505 electronic cigarette product rules."""

    ref_id: str = "UT-ECIG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class UtSpecialtyPermitCheck:
    """Utah general tobacco vs retail tobacco specialty business permit check."""

    ref_id: str = "UT-PERMIT-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def check_ut_nicotine_volume_cap(nicotine_mg_ml: float, cap_mg_ml: float = 36.0) -> dict:
    """Check e-liquid nicotine concentration against Utah 36 mg/mL (3%) cap."""
    if not isinstance(nicotine_mg_ml, (int, float)) or nicotine_mg_ml < 0 or cap_mg_ml <= 0:
        raise DataValidationError("Invalid nicotine_mg_ml")
    return {"op": "check_ut_nicotine_volume_cap", "compliant": float(nicotine_mg_ml) <= float(cap_mg_ml), "src": "recallstorm/states/ut_cotinine_nicotine.py"}


def evaluate_ut_flavor_restriction(flavor: str, is_specialty_store: bool = False) -> dict:
    """Evaluate Utah restriction on non-tobacco/non-menthol e-cigarette flavors in general grocery stores."""
    _req(flavor, "flavor")
    flv = str(flavor).lower()
    allowed = is_specialty_store or flv in {"tobacco", "menthol", "unflavored"}
    return {"op": "evaluate_ut_flavor_restriction", "flavor": flv, "allowed": allowed, "src": "recallstorm/states/ut_cotinine_nicotine.py"}


def verify_ut_tax_stamp_presence(sku_id: str, stamped: bool = True) -> dict:
    """Verify Utah Tax Commission electronic cigarette tax compliance."""
    _req(sku_id, "sku_id")
    return {"op": "verify_ut_tax_stamp_presence", "sku_id": str(sku_id), "compliant": bool(stamped), "src": "recallstorm/states/ut_cotinine_nicotine.py"}


def flag_ut_unauthorized_vape_skus(skus: list[str]) -> list[str]:
    """Return sorted unauthorized vape SKU IDs in Utah."""
    if skus is None:
        raise DataValidationError("skus cannot be None")
    return sorted(str(s) for s in skus if str(s).strip())


def parse_ut_dhhs_banned_list(notice_id: str) -> dict:
    """Parse Utah DHHS prohibited electronic cigarette product list."""
    _req(notice_id, "notice_id")
    return {"op": "parse_ut_dhhs_banned_list", "notice_id": str(notice_id), "state": "UT", "src": "recallstorm/states/ut_cotinine_nicotine.py"}


def build_ut_cage_removal_task(store_id: str, sku_id: str) -> dict:
    """Build a front-end tobacco cage removal task for a Utah store."""
    _req(store_id, "store_id")
    _req(sku_id, "sku_id")
    return {"op": "build_ut_cage_removal_task", "store_id": str(store_id), "sku_id": str(sku_id), "src": "recallstorm/states/ut_cotinine_nicotine.py"}


def filter_ut_front_end_fixtures(fixtures: list[str]) -> list[str]:
    """Filter front-end tobacco fixtures in Utah stores."""
    if fixtures is None:
        raise DataValidationError("fixtures cannot be None")
    return sorted(str(f) for f in fixtures if str(f).strip())


def calculate_ut_revocation_risk(violations: int) -> dict:
    """Assess Utah tobacco permit suspension/revocation risk from violations within 24 months."""
    if not isinstance(violations, int) or violations < 0:
        raise DataValidationError("violations must be non-negative int")
    return {"op": "calculate_ut_revocation_risk", "high_risk": violations >= 3, "violations": violations, "src": "recallstorm/states/ut_cotinine_nicotine.py"}


def validate_ut_wholesaler_invoice(invoice_id: str, licensed: bool = True) -> dict:
    """Validate that tobacco/nicotine inventory was purchased from a licensed Utah wholesaler."""
    _req(invoice_id, "invoice_id")
    return {"op": "validate_ut_wholesaler_invoice", "invoice_id": str(invoice_id), "valid": bool(licensed), "src": "recallstorm/states/ut_cotinine_nicotine.py"}


def audit_ut_age_scanner_logs(store_id: str, scan_pct: float = 100.0) -> dict:
    """Audit electronic 21+ ID scanner logs in Utah stores."""
    _req(store_id, "store_id")
    if not (0.0 <= scan_pct <= 100.0):
        raise DataValidationError("scan_pct must be in [0, 100]")
    return {"op": "audit_ut_age_scanner_logs", "store_id": str(store_id), "compliant": scan_pct >= 99.0, "src": "recallstorm/states/ut_cotinine_nicotine.py"}
