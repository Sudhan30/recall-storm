"""Property tests for recallstorm.core.errors."""
import random
from recallstorm.core.errors import (
    AllocationError,
    DataValidationError,
    LaborError,
    RoutingError,
    RuleConfigError,
    ScenarioError,
    error_to_record,
    format_error,
)


def test_error_serialization_determinism():
    rng = random.Random(42)
    classes = [
        DataValidationError,
        RuleConfigError,
        AllocationError,
        RoutingError,
        LaborError,
        ScenarioError,
    ]
    for i in range(30):
        cls = rng.choice(classes)
        msg = f"msg_{i}_{rng.randint(1, 1000)}"
        err = cls(msg, {"idx": i})
        assert format_error(err) == format_error(err)
        r1 = error_to_record(err)
        r2 = error_to_record(err)
        assert r1 == r2
        assert r1["details"]["idx"] == i
