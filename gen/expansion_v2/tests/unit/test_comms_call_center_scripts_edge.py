"""Edge case tests for recallstorm.comms.call_center_scripts."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.comms.call_center_scripts import (
    generate_daily_sentiment_digest,
    provide_instant_e_gift_card_issuance,
)


def test_call_center_scripts_edge():
    with pytest.raises(DataValidationError):
        provide_instant_e_gift_card_issuance("C1", 1000.0)
    with pytest.raises(DataValidationError):
        generate_daily_sentiment_digest(10, 20)
