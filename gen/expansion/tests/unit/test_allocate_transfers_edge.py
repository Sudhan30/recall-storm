"""Edge tests for recallstorm.allocate.transfers."""
import pytest
from recallstorm.allocate.transfers import (
    transfer_handoff,
    validate_transfers,
)


def test_transfers_edge():
    with pytest.raises(TypeError):
        transfer_handoff("not_alloc", ("a", "b"))  # type: ignore[arg-type]
    bad_h = {"handoff_id": "H1", "kind": "SUB_TRANSFER", "ref_ids": ["MISSING_ALC"]}
    assert validate_transfers([bad_h], []) != []
