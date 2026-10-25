"""Exception hierarchy and error formatting utilities."""
from __future__ import annotations


class RecallStormError(Exception):
    """Base exception for all Recall Storm errors."""

    def __init__(self, message: str, code: str = "RECALLSTORM_ERROR", details: dict | None = None):
        super().__init__(message)
        self.message = str(message)
        self.code = str(code)
        self.details = dict(details) if details else {}


class DataValidationError(RecallStormError):
    """Raised when input data fails schema or invariant validation."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="DATA_VALIDATION_ERROR", details=details)


class RuleConfigError(RecallStormError):
    """Raised when regulatory rules are invalid or misconfigured."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="RULE_CONFIG_ERROR", details=details)


class AllocationError(RecallStormError):
    """Raised when substitute stock allocation fails or violates conservation."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="ALLOCATION_ERROR", details=details)


class RoutingError(RecallStormError):
    """Raised when return routing or truck packing fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="ROUTING_ERROR", details=details)


class LaborError(RecallStormError):
    """Raised when associate shift or floater assignment fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="LABOR_ERROR", details=details)


class ScenarioError(RecallStormError):
    """Raised when a scenario file or configuration is invalid."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="SCENARIO_ERROR", details=details)


def format_error(err: Exception) -> str:
    """Format an exception into a structured single-line diagnostic string."""
    if not isinstance(err, Exception):
        raise TypeError("err must be an Exception instance")
    if isinstance(err, RecallStormError):
        return f"[{err.code}] {err.message}"
    return f"[{err.__class__.__name__}] {err}"


def error_to_record(err: Exception, src: str = "recallstorm/core/errors.py") -> dict:
    """Convert an exception into a serializable dictionary record."""
    if not isinstance(err, Exception):
        raise TypeError("err must be an Exception instance")
    if isinstance(err, RecallStormError):
        return {
            "type": "error",
            "code": err.code,
            "message": err.message,
            "details": err.details,
            "src": src,
        }
    return {
        "type": "error",
        "code": err.__class__.__name__,
        "message": str(err),
        "details": {},
        "src": src,
    }
