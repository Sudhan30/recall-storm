"""Custom exception hierarchy and error formatting for Recall Storm."""
from __future__ import annotations


class RecallStormError(Exception):
    """Base exception for all Recall Storm platform errors."""

    code: str = "RECALLSTORM_ERROR"

    def __init__(self, message: str, details: dict | None = None) -> None:
        if not isinstance(message, str) or not message.strip():
            message = "Unspecified RecallStormError"
        super().__init__(message)
        self.message = message
        self.details = dict(details) if details else {}


class DataValidationError(RecallStormError):
    """Raised when input records or DataPack entities fail validation."""

    code: str = "DATA_VALIDATION_ERROR"


class RuleConfigError(RecallStormError):
    """Raised when rule definitions, dates, or jurisdictions are invalid."""

    code: str = "RULE_CONFIG_ERROR"


class AllocationError(RecallStormError):
    """Raised when substitute stock allocation fails or violates conservation."""

    code: str = "ALLOCATION_ERROR"


class RoutingError(RecallStormError):
    """Raised when return routing or truck packing fails."""

    code: str = "ROUTING_ERROR"


class LaborError(RecallStormError):
    """Raised when associate shift or labor compliance constraints fail."""

    code: str = "LABOR_ERROR"


class ScenarioError(RecallStormError):
    """Raised when a scenario configuration or file is invalid."""

    code: str = "SCENARIO_ERROR"


def format_error(exc: BaseException) -> str:
    """Format an exception into a structured single-line string."""
    if not isinstance(exc, BaseException):
        raise TypeError("exc must be a BaseException instance")
    if isinstance(exc, RecallStormError):
        if exc.details:
            kv = ", ".join(f"{k}={v}" for k, v in sorted(exc.details.items()))
            return f"[{exc.code}] {exc.message} ({kv})"
        return f"[{exc.code}] {exc.message}"
    return f"[{exc.__class__.__name__}] {exc}"


def error_to_record(exc: BaseException, src: str = "recallstorm/core/errors.py") -> dict:
    """Serialize an exception to a dictionary record with provenance."""
    if not isinstance(exc, BaseException):
        raise TypeError("exc must be a BaseException instance")
    if not isinstance(src, str) or not src.strip():
        raise ValueError("src must be a non-empty string")
    if isinstance(exc, RecallStormError):
        return {
            "type": "error",
            "code": exc.code,
            "message": exc.message,
            "details": dict(exc.details),
            "src": src.strip(),
        }
    return {
        "type": "error",
        "code": exc.__class__.__name__,
        "message": str(exc),
        "details": {},
        "src": src.strip(),
    }
