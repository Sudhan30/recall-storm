"""Edge case tests for recallstorm.pricing.markdown_controls."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.pricing.markdown_controls import (
    flag_suspicious_pre_recall_markdowns,
    reconcile_markdown_journal_reversals,
)


def test_markdown_controls_edge():
    with pytest.raises(DataValidationError):
        flag_suspicious_pre_recall_markdowns("WM1", 120.0)
    with pytest.raises(DataValidationError):
        reconcile_markdown_journal_reversals(-1, 2.0)
