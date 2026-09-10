import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent / "src"))

_FIXTURES = Path(__file__).parent / "tests" / "fixtures"


def pytest_collection_modifyitems(config, items):
    """Skip fixture-dependent tests when no local UEFN fixtures are present.

    Fixtures are copies of the user's own UEFN project files (Epic content), so
    they are not distributed with the repo. A fresh clone therefore runs only
    the tests that need no fixtures; see README "테스트".
    """
    if _FIXTURES.exists() and any(_FIXTURES.rglob("*.uasset")):
        return
    skip = pytest.mark.skip(
        reason="no local UEFN fixtures (tests/fixtures/*.uasset) — see README"
    )
    for item in items:
        src = item.fspath.purebasename
        if src in {
            "test_uasset", "test_level", "test_properties", "test_index",
            "test_graph", "test_query", "test_settings", "test_analyze",
            "test_m6", "test_m7b", "test_structure", "test_spatial",
            "test_verse", "test_verse_source", "test_write",
            "test_write_versevm", "test_patch", "test_rebuild", "test_cli",
        }:
            item.add_marker(skip)
