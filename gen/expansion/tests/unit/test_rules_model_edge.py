"""Edge tests for recallstorm.rules.model."""
import pytest
from recallstorm.core.errors import RuleConfigError
from recallstorm.rules.model import (
    effective_local,
    load_rules,
    rule_by_id,
)


def test_model_edge():
    rs = load_rules([])
    with pytest.raises(RuleConfigError):
        rule_by_id(rs, "MISSING")
    with pytest.raises(RuleConfigError):
        load_rules(123)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        effective_local("not_rule")  # type: ignore[arg-type]
