"""Edge tests for recallstorm.cli.main."""
from recallstorm.cli.main import exit_code_for, main
from recallstorm.core.errors import RecallStormError


def test_cli_edge_errors(tmp_path):
    assert main(["run", "--scenario", "nonexistent_scenario", "--data", "data", "--out", str(tmp_path)]) == 2
    assert main(["scenarios", "--data", str(tmp_path / "missing_dir")]) == 2
    assert exit_code_for(RecallStormError("err")) == 4
    assert exit_code_for(RuntimeError("err")) == 1
