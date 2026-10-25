"""Unit tests for recallstorm.core.errors."""
from recallstorm.core.errors import (
    AllocationError,
    DataValidationError,
    LaborError,
    RecallStormError,
    RoutingError,
    RuleConfigError,
    ScenarioError,
    error_to_record,
    format_error,
)


def test_error_hierarchy():
    errors = [
        RecallStormError("base"),
        DataValidationError("bad sku", {"sku_id": "X"}),
        RuleConfigError("bad rule"),
        AllocationError("negative stock"),
        RoutingError("overweight"),
        LaborError("no shift"),
        ScenarioError("missing file"),
    ]
    for e in errors:
        assert isinstance(e, RecallStormError)
        formatted = format_error(e)
        assert e.code in formatted
        rec = error_to_record(e)
        assert rec["code"] == e.code
        assert rec["src"] == "recallstorm/core/errors.py"
