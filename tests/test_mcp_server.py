import importlib.util
from pathlib import Path

import pytest

from _synth import actor_package, device_package

ROOT = Path(__file__).parent.parent


def _load_server():
    spec = importlib.util.spec_from_file_location("mcp_server", ROOT / "mcp_server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_mcp_server_registers_expected_tools():
    mod = _load_server()
    tools = set(mod.mcp._tool_manager._tools.keys())
    assert {"inspect_level", "find", "who_uses", "read_actor",
            "editable_bindings", "engine_devices", "bind_editable"} <= tools


def _layout(tmp_path):
    dev = tmp_path / "Proj/Content/__ExternalActors__/MyProject/0/AA/DEV.uasset"
    light = tmp_path / "Proj/Content/__ExternalActors__/MyProject/0/EC/LIGHTPKG.uasset"
    for f, blob in ((dev, device_package()), (light, actor_package())):
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(blob)
    return dev, light


def test_bind_editable_tool_wires_slot_from_actor_file(tmp_path, monkeypatch):
    mod = _load_server()
    monkeypatch.setattr(mod, "_editor_running", lambda: (False, "test: no listener"))
    dev, light = _layout(tmp_path)

    out = mod.bind_editable(str(dev), "Trigger", str(light))

    assert out["status"] == "ok"
    assert out["target"]["actor_name"] == "Device_PointLight_V2_C_UAID_AAAA000000000000_1"
    assert out["target"]["actor_package_name"] == "/MyProject/__ExternalActors__/MyProject/0/EC/LIGHTPKG"
    assert out["bindings"]["Trigger"] == "Device_PointLight_V2_C_UAID_AAAA000000000000"
    assert Path(out["backup"]).exists()
    assert mod.editable_bindings(str(dev))["Trigger"] == "Device_PointLight_V2_C_UAID_AAAA000000000000"


def test_bind_editable_tool_refuses_while_editor_is_open(tmp_path, monkeypatch):
    mod = _load_server()
    monkeypatch.setattr(mod, "_editor_running", lambda: (True, "test: listener on :8765"))
    dev, light = _layout(tmp_path)
    before = dev.read_bytes()

    out = mod.bind_editable(str(dev), "Trigger", str(light))

    assert out["status"] == "blocked"
    assert dev.read_bytes() == before
    assert not dev.with_suffix(".uasset.bak").exists()


def test_bind_editable_tool_reports_unknown_slot_without_touching_file(tmp_path, monkeypatch):
    mod = _load_server()
    monkeypatch.setattr(mod, "_editor_running", lambda: (False, "test"))
    dev, light = _layout(tmp_path)
    before = dev.read_bytes()
    with pytest.raises(Exception):
        mod.bind_editable(str(dev), "Nope", str(light))
    assert dev.read_bytes() == before
