import importlib.util
from pathlib import Path

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
            "editable_bindings", "engine_devices"} <= tools
