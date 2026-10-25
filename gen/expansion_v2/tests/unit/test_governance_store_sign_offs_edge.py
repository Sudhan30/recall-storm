"""Edge case tests for recallstorm.governance.store_sign_offs."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.governance.store_sign_offs import (
    flag_proxy_sign_offs_by_unauthorized_staff,
    validate_100_percent_aisle_task_completion,
)


def test_store_sign_offs_edge():
    assert flag_proxy_sign_offs_by_unauthorized_staff("TEMPORARY_CLERK")["authorized"] is False
    with pytest.raises(DataValidationError):
        validate_100_percent_aisle_task_completion(15, 10)
