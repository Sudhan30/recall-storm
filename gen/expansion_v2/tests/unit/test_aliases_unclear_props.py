"""Property tests for recallstorm.aliases.unclear."""
from recallstorm.aliases.unclear import is_generic_color


def test_specific_dyes_override_generic_color():
    for dye in ("RED 40", "YELLOW 5", "BLUE 1", "CARMINE", "ANNATTO", "CARAMEL COLOR"):
        txt = f"SUGAR, WATER, ARTIFICIAL COLOR ({dye}), SALT."
        assert is_generic_color(txt) is False
