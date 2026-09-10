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
    needs_fixtures: dict[str, bool] = {}
    for item in items:
        path = str(getattr(item, "path", None) or item.fspath)
        if path not in needs_fixtures:
            # A module needs fixtures if its source mentions the fixtures dir.
            try:
                text = Path(path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            needs_fixtures[path] = "fixtures" in text
        if needs_fixtures[path]:
            item.add_marker(skip)
