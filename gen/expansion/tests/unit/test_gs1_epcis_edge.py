"""Edge tests for recallstorm.gs1.epcis."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.epcis import (
    epc_to_gtin,
    parse_epcis_event,
)


def test_epcis_edge():
    with pytest.raises(DataValidationError):
        epc_to_gtin("urn:invalid")
    with pytest.raises(DataValidationError):
        parse_epcis_event({})
