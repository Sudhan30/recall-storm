"""Edge tests for recallstorm.core.registry."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.core.registry import (
    get_module,
    register_module,
    reset_registry,
)


def test_registry_errors():
    reset_registry()
    with pytest.raises(DataValidationError):
        get_module("missing")
    with pytest.raises(ValueError):
        register_module("", "path.py")
    with pytest.raises(ValueError):
        register_module("mod", "")
    with pytest.raises(ValueError):
        register_module("mod", "path.py", "")
