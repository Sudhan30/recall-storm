"""Edge case tests for recallstorm.comms.vendor_notices."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.comms.vendor_notices import (
    issue_formal_notice_of_quarantine,
    log_vendor_disposition_instructions,
)


def test_vendor_notices_edge():
    with pytest.raises(DataValidationError):
        issue_formal_notice_of_quarantine("V1", [])
    with pytest.raises(DataValidationError):
        log_vendor_disposition_instructions("V1", "SELL_ANYWAY")
