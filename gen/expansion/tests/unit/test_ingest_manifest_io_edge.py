"""Edge tests for recallstorm.ingest.manifest_io."""
import pytest
from recallstorm.core.errors import DataValidationError
from recallstorm.ingest.manifest_io import (
    datapack_stats,
    load_datapack_extended,
    sample_datapack,
    write_datapack,
)


def test_manifest_io_edge(tmp_path):
    with pytest.raises(DataValidationError):
        load_datapack_extended(tmp_path / "nonexistent")
    with pytest.raises(TypeError):
        write_datapack("not_a_pack", tmp_path)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        datapack_stats("not_a_pack")  # type: ignore[arg-type]
    pack = load_datapack_extended("data")
    with pytest.raises(ValueError):
        sample_datapack(pack, 0)
