"""Edge case tests for recallstorm.cli.main."""
from recallstorm.cli.main import cmd_explain, cmd_scenarios, main
from recallstorm.core.jsonl import write_jsonl


def test_cli_main_edge(tmp_path):
    assert main([]) == 1
    assert cmd_scenarios(str(tmp_path / "missing_dir")) == 1
    p = tmp_path / "plan.jsonl"
    write_jsonl(str(p), [{"type": "run", "run_id": "R1"}])
    assert cmd_explain(str(p), "MISSING_SKU") == 1
