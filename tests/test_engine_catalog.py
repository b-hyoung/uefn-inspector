from uefn_inspector.engine_catalog import load_engine_catalog, search_engine_devices


def test_engine_catalog_loads():
    cat = load_engine_catalog()
    assert cat["deviceCount"] > 1000
    assert len(cat["devices"]) == cat["deviceCount"]


def test_search_engine_devices():
    hits = search_engine_devices("AudioPlayer")
    assert "Device_CRD_AudioPlayer" in hits
