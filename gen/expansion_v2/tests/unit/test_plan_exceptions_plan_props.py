"""Property tests for recallstorm.plan.exceptions_plan."""
from contract import StoreNote
from recallstorm.core.jsonl import validate_record
from recallstorm.plan.exceptions_plan import exception_records


def test_exception_records_schema_props():
    notes = [StoreNote(f"N{i}", f"WM{i}", "Online pickup totes staged") for i in range(15)]
    recs = exception_records(notes, {})
    for r in recs:
        assert validate_record(r, "exception") == []
