"""Property tests for recallstorm.store.exceptions."""
from contract import ExceptionKind, StoreNote
from recallstorm.store.exceptions import note_to_exception


def test_note_to_exception_enum_validity():
    valid_kinds = {k.value for k in ExceptionKind}
    for i, txt in enumerate(["DSD rep", "Endcap 4", "Topstock", "pickup totes", "remodel", "smudged"]):
        rec = note_to_exception(StoreNote(f"N{i}", "WM1", txt))
        assert rec["kind"] in valid_kinds
