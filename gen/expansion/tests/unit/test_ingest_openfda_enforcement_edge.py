"""Edge tests for recallstorm.ingest.openfda_enforcement."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.openfda_enforcement import (
    classify_recall_reason,
    extract_lot_codes,
    parse_enforcement_report,
    recall_jurisdictions,
)


def test_openfda_edge():
    with pytest.raises(DataValidationError):
        parse_enforcement_report({})
    assert extract_lot_codes("") == []
    assert recall_jurisdictions("Nationwide distribution") == ["US"]
    assert classify_recall_reason("Salmonella contamination") == "PATHOGEN"
    assert classify_recall_reason("Undeclared milk") == "UNDECLARED_ALLERGEN"
    assert classify_recall_reason("Foreign plastic") == "OTHER"
