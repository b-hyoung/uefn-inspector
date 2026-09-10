import pytest

from uefn_inspector.analysis.engine_catalog import (
    CatalogMissing,
    load_engine_catalog,
    search_engine_devices,
)


def _catalog_or_skip():
    try:
        return load_engine_catalog()
    except CatalogMissing:
        pytest.skip("engine catalog not generated on this machine (see cue4parse_cli/README.md)")


def test_engine_catalog_loads():
    cat = _catalog_or_skip()
    assert cat["deviceCount"] > 1000
    assert len(cat["devices"]) == cat["deviceCount"]


def test_search_engine_devices():
    _catalog_or_skip()
    assert "Device_CRD_AudioPlayer" in search_engine_devices("AudioPlayer")


def test_missing_catalog_gives_actionable_error(tmp_path):
    with pytest.raises(CatalogMissing) as e:
        load_engine_catalog(tmp_path / "nope.json")
    assert "cue4parse_cli/README.md" in str(e.value)
