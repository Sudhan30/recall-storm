"""Edge case tests for recallstorm.core.registry."""
import pytest
from recallstorm.core.registry import emit_with_src, register_module, reset_registry, src_path_for


def test_registry_edge():
    reset_registry()
    assert src_path_for("recallstorm.plan.tasks") == "recallstorm/plan/tasks.py"
    assert src_path_for("recallstorm/plan/tasks.py") == "recallstorm/plan/tasks.py"
    with pytest.raises(ValueError):
        register_module("", "a.py")
    with pytest.raises(ValueError):
        register_module("a", "")
    with pytest.raises(TypeError):
        emit_with_src("not_dict", "a")  # type: ignore[arg-type]
