"""Edge case tests for recallstorm.comms.translation_localization."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.comms.translation_localization import (
    audit_translation_turnaround_sla,
    check_reading_grade_level_simplicity,
)


def test_translation_localization_edge():
    with pytest.raises(DataValidationError):
        check_reading_grade_level_simplicity(0.0)
    with pytest.raises(DataValidationError):
        audit_translation_turnaround_sla(-1.0)
