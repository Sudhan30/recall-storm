"""Detect pencil-whipping scans, zero-find anomalies, and clock drift."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class PullScanAnomalyDetector:
    """Detector for fraudulent or anomalous store recall pull scans."""

    ref_id: str = "ANM-DET-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class FraudAndErrorFlag:
    """Audit flag for store compliance anomalies."""

    ref_id: str = "ANM-FLG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def detect_impossible_speed_pencil_whipping(tasks_completed: int, elapsed_seconds: float) -> dict:
    """Flag 'pencil-whipping' when an associate marks multiple aisle pulls DONE in < 5 seconds per task."""
    if tasks_completed <= 0 or elapsed_seconds < 0:
        raise DataValidationError("Invalid tasks_completed or elapsed_seconds")
    secs_per_task = elapsed_seconds / tasks_completed
    return {"op": "detect_impossible_speed_pencil_whipping", "pencil_whipped": secs_per_task < 5.0, "secs_per_task": round(secs_per_task, 2), "src": "recallstorm/analytics/anomaly_detection.py"}


def flag_zero_unit_found_in_high_on_hand_store(book_on_hand: int, physical_found: int, threshold: int = 24) -> dict:
    """Flag stores reporting 0 units found when perpetual inventory shows >= threshold units on hand."""
    if book_on_hand < 0 or physical_found < 0 or threshold <= 0:
        raise DataValidationError("Invalid inventory counts")
    anomaly = (physical_found == 0) and (book_on_hand >= threshold)
    return {"op": "flag_zero_unit_found_in_high_on_hand_store", "anomaly": anomaly, "book_on_hand": int(book_on_hand), "src": "recallstorm/analytics/anomaly_detection.py"}


def identify_unusual_post_lock_pos_override_scans(store_id: str, blocked_scans_after_signoff: int) -> dict:
    """Flag stores where customers attempt to buy recalled items at POS AFTER the manager attested 100% shelf pull."""
    _req(store_id, "store_id")
    if blocked_scans_after_signoff < 0:
        raise DataValidationError("blocked_scans_after_signoff cannot be negative")
    return {"op": "identify_unusual_post_lock_pos_override_scans", "store_id": str(store_id), "missed_shelf_stock": blocked_scans_after_signoff > 0, "src": "recallstorm/analytics/anomaly_detection.py"}


def spot_outlier_destruction_weight_variances(expected_lb: float, weighed_lb: float, max_var_pct: float = 0.15) -> dict:
    """Spot destruction weight outliers exceeding 15% variance."""
    if expected_lb <= 0 or weighed_lb < 0 or max_var_pct <= 0:
        raise DataValidationError("Invalid weights")
    var_pct = abs(weighed_lb - expected_lb) / expected_lb
    return {"op": "spot_outlier_destruction_weight_variances", "outlier": var_pct > max_var_pct, "var_pct": round(var_pct, 4), "src": "recallstorm/analytics/anomaly_detection.py"}


def detect_coordinated_multi_store_scan_gaps(stores_with_gaps: list[str], district: str) -> dict:
    """Detect district-wide communication or price-file gaps."""
    if stores_with_gaps is None:
        raise DataValidationError("stores_with_gaps cannot be None")
    _req(district, "district")
    return {"op": "detect_coordinated_multi_store_scan_gaps", "district": str(district), "systemic_gap": len(stores_with_gaps) >= 3, "src": "recallstorm/analytics/anomaly_detection.py"}


def alert_on_after_hours_quarantine_bin_access(store_id: str, hour_24: int, authorized: bool = False) -> dict:
    """Alert Asset Protection on unauthorized quarantine cage access."""
    _req(store_id, "store_id")
    if not (0 <= hour_24 <= 23):
        raise DataValidationError("hour_24 must be in 0..23")
    return {"op": "alert_on_after_hours_quarantine_bin_access", "store_id": str(store_id), "alert": not authorized, "src": "recallstorm/analytics/anomaly_detection.py"}


def compare_sister_store_pull_ratios_by_cluster(store_ratio: float, cluster_median: float) -> dict:
    """Flag stores whose pull ratio deviates by more than 0.50 from peer cluster median."""
    if not (0.0 <= store_ratio <= 1.0) or not (0.0 <= cluster_median <= 1.0):
        raise DataValidationError("Ratios must be in [0, 1]")
    return {"op": "compare_sister_store_pull_ratios_by_cluster", "deviant": abs(store_ratio - cluster_median) > 0.50, "src": "recallstorm/analytics/anomaly_detection.py"}


def isolate_handheld_scanner_clock_drift_errors(ntp_offset_secs: float, max_drift_secs: float = 60.0) -> dict:
    """Identify RF handhelds with NTP clock drift exceeding max_drift_secs."""
    if max_drift_secs <= 0:
        raise DataValidationError("max_drift_secs must be positive")
    return {"op": "isolate_handheld_scanner_clock_drift_errors", "clock_drifted": abs(ntp_offset_secs) > max_drift_secs, "src": "recallstorm/analytics/anomaly_detection.py"}


def score_store_submission_credibility_index(anomalies_found: int) -> float:
    """Compute a credibility score in [0.0, 100.0] deducting 25 points per anomaly."""
    if anomalies_found < 0:
        raise DataValidationError("anomalies_found cannot be negative")
    return float(max(0, 100 - anomalies_found * 25))


def route_flagged_anomalies_to_audit_queue(store_ids: list[str]) -> list[str]:
    """Route flagged store_ids to the QA/LP audit queue."""
    if store_ids is None:
        raise DataValidationError("store_ids cannot be None")
    return sorted(set(str(s) for s in store_ids if str(s).strip()))
