"""Edge case tests for recallstorm.governance.retention_policies."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.governance.retention_policies import (
    apply_seven_year_fda_fsma_retention_rule,
    link_related_vendor_correspondence_to_hold,
)


def test_retention_policies_edge():
    with pytest.raises(DataValidationError):
        apply_seven_year_fda_fsma_retention_rule("2026-12-30", 1)
    with pytest.raises(DataValidationError):
        link_related_vendor_correspondence_to_hold("MAT1", [])
