from pathlib import Path

from uefn_inspector.model.index import build_index

LEVEL_DIR = Path(__file__).parent / "fixtures" / "level"


def test_build_index_parses_all_packages():
    idx = build_index(LEVEL_DIR)
    assert len(idx.packages) == 3
    for pkg in idx.packages.values():
        assert pkg.imports
        assert pkg.exports
