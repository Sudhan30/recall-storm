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


def test_exception_hierarchy():
    classes = [
        DataValidationError,
        RuleConfigError,
        AllocationError,
        RoutingError,
        LaborError,
        ScenarioError,
    ]
    for cls in classes:
        inst = cls("something went wrong", {"id": "X1"})
        assert isinstance(inst, RecallStormError)
        assert inst.message == "something went wrong"
        assert inst.details == {"id": "X1"}


def test_format_error():
    e = DataValidationError("bad sku", {"sku_id": "S1"})
    formatted = format_error(e)
    assert "[DATA_VALIDATION_ERROR] bad sku (sku_id=S1)" == formatted


def test_error_to_record():
    e = RoutingError("truck full", {"truck_id": "T0"})
    rec = error_to_record(e, "recallstorm/route/packing.py")
    assert rec["code"] == "ROUTING_ERROR"
    assert rec["message"] == "truck full"
    assert rec["details"] == {"truck_id": "T0"}
    assert rec["src"] == "recallstorm/route/packing.py"
