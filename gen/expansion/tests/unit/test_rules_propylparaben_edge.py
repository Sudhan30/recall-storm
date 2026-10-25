"""Edge tests for recallstorm.rules.propylparaben."""
from datetime import datetime, timezone
import pytest
from contract import Sku, Verdict
from recallstorm.rules.propylparaben import evaluate_propylparaben


def test_propylparaben_edge():
    sku = Sku("P1", "00012345678905", "Lotion", "Brand", "cosmetic", "PROPYLPARABEN", False, False, 12, 1.0, 5.0)
    dec = evaluate_propylparaben(sku, datetime(2027, 1, 2, tzinfo=timezone.utc))
    assert dec.verdict == Verdict.KEEP
    with pytest.raises(TypeError):
        evaluate_propylparaben("not_sku", datetime(2027, 1, 1))  # type: ignore[arg-type]
