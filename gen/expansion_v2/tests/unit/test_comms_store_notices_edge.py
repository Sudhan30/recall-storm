"""Edge case tests for recallstorm.comms.store_notices."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.comms.store_notices import (
    compile_single_page_store_action_sheet,
    version_control_amended_recall_notices,
)


def test_store_notices_edge():
    with pytest.raises(DataValidationError):
        compile_single_page_store_action_sheet("WM1", [])
    with pytest.raises(DataValidationError):
        version_control_amended_recall_notices("REC1", 0)
