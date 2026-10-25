"""Unit tests for recallstorm.core.registry."""
from recallstorm.core.registry import (
    Registry,
    emit_with_src,
    get_module,
    list_modules,
    module_version,
    register_module,
    registry_snapshot,
    reset_registry,
    src_path_for,
)


def test_registry_operations():
    reset_registry()
    reg = Registry()
    assert reg.modules == {}
    entry = register_module("recallstorm.rules.engine", "recallstorm/rules/engine.py", "1.2.0")
    assert entry["src"] == "recallstorm/rules/engine.py"
    assert get_module("recallstorm.rules.engine") == entry
    assert list_modules() == ["recallstorm.rules.engine"]
    assert src_path_for("recallstorm.rules.engine") == "recallstorm/rules/engine.py"
    assert module_version("recallstorm.rules.engine") == "1.2.0"
    rec = emit_with_src({"type": "run"}, "recallstorm.rules.engine")
    assert rec["src"] == "recallstorm/rules/engine.py"
    snap = registry_snapshot()
    assert "recallstorm.rules.engine" in snap
