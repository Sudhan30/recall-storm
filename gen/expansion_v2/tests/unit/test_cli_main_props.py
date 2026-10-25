"""Property tests for recallstorm.cli.main."""
from recallstorm.cli.main import build_parser


def test_parser_subcommands_props():
    parser = build_parser()
    for sub in ("run", "validate", "stats", "explain", "replay", "scenarios"):
        assert sub in parser.format_help()
