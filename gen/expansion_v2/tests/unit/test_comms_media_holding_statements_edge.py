"""Edge case tests for recallstorm.comms.media_holding_statements."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.comms.media_holding_statements import (
    brief_executive_spokesperson_q_and_a,
    flag_viral_tiktok_product_complaints,
)


def test_media_holding_statements_edge():
    with pytest.raises(DataValidationError):
        flag_viral_tiktok_product_complaints("V1", -1)
    with pytest.raises(DataValidationError):
        brief_executive_spokesperson_q_and_a("R1", [])
