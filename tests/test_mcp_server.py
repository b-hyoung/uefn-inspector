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


def test_mcp_server_ships_offline_first_instructions():
    """The leash: the host injects `instructions` into every session's system
    prompt, so it must name the gate (`capabilities`) and the write tool."""
    mod = _load_server()
    text = mod.mcp.instructions
    assert text and "capabilities" in text and "bind_editable" in text
    assert "GUI only" in text and "not valid ScriptDevice" in text


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


def test_level_map_tool_returns_map_zones_and_brief_template(monkeypatch):
    from uefn_inspector.level import Level, PlacedActor
    mod = _load_server()
    fake = Level(name="L", actors=[
        PlacedActor("Device_PlayerSpawner_C", "PS_UAID_1", (0.0, 0.0, 0.0)),
        PlacedActor("Device_GuardSpawner_C", "GS_UAID_1", (3000.0, 0.0, 0.0)),
        PlacedActor("Device_GuardSpawner_C", "GS_UAID_2", (3500.0, 500.0, 0.0)),
        PlacedActor("GrayBox_Wall_C", "W_UAID_1", None),          # no location: listed, not mapped
    ])
    monkeypatch.setattr(mod, "_inspect_level", lambda path: fake)

    out = mod.level_map("any/dir", cell=500)

    assert out["actors"] == 4 and out["placed"] == 3
    assert out["unplaced"] == ["GrayBox_Wall_C W_UAID_1"]
    zones = {z["class"]: z for z in out["zones"]}
    assert zones["Device_GuardSpawner_C"]["count"] == 2
    assert zones["Device_GuardSpawner_C"]["centroid"] == (3250.0, 250.0, 0.0)
    assert zones["Device_GuardSpawner_C"]["x_range"] == (3000.0, 3500.0)
    assert out["extent"] == (3500.0, 500.0, 0.0)
    assert out["legend"]["G"] == "Device_GuardSpawner_C" and "P" in out["map"]
    assert set(out["brief_template"]) >= {"theme", "zones", "flow", "screenshots"}
