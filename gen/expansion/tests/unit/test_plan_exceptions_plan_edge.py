"""Edge tests for recallstorm.plan.exceptions_plan."""
import pytest
from recallstorm.plan.exceptions_plan import exception_tasks


def test_exceptions_plan_edge():
    with pytest.raises(TypeError):
        exception_tasks("not_note", [])  # type: ignore[arg-type]
