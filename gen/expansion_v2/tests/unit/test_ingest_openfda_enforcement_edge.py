"""Edge case tests for recallstorm.ingest.openfda_enforcement."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.openfda_enforcement import classify_recall_reason, parse_enforcement_report


def test_openfda_edge():
    with pytest.raises(DataValidationError):
        parse_enforcement_report({})
    assert classify_recall_reason("Listeria monocytogenes") == "MICROBIAL"
    assert classify_recall_reason("Metal fragments") == "FOREIGN_MATERIAL"
    assert classify_recall_reason("Packaging defect") == "OTHER"
