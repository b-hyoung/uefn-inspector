"""MCP server for uefn-inspector — exposes the offline analyses as tools any
Claude session can call. Complements the live uefn/unreal MCPs (which need the
editor open and cannot read Verse-VM data): this one reads/analyses the project
files directly, editor open or closed.

Run:  <py> mcp_server.py        (stdio MCP server)
Register (Claude Code):
  claude mcp add uefn-inspector -s user -- <py> <abs path>/mcp_server.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from uefn_inspector.analysis.analyze import impact  # noqa: E402
from uefn_inspector.capabilities import probe as _probe  # noqa: E402
from uefn_inspector.cli import run  # noqa: E402
from uefn_inspector.analysis.engine_catalog import search_engine_devices  # noqa: E402
from uefn_inspector.model.index import build_index  # noqa: E402
from uefn_inspector.level import audit_level  # noqa: E402
from uefn_inspector.core.properties import decode_properties  # noqa: E402
from uefn_inspector.analysis.query import search, where_used  # noqa: E402
from uefn_inspector.core.uasset import read_package  # noqa: E402
from uefn_inspector.analysis.verse import verse_bindings  # noqa: E402

mcp = FastMCP("uefn-inspector")


@mcp.tool()
def capabilities(sample_file: str = "") -> dict:
    """What this tool can ACTUALLY do right now — every entry verified by running
    it, not read from documentation. Call this before claiming something is or
    isn't possible. Pass a placed-actor .uasset as `sample_file` for a full check
    (bindings, property decode, size-changing edit); without it those report
    "unverified". Also reports preconditions: editor open (blocks offline writes),
    catalog present, live MCP reachable."""
    return _probe(sample_file or None)


@mcp.tool()
def inspect_level(path: str) -> dict:
    """Offline inventory of a UEFN level/actor directory: device counts, asset
    refs, warnings. `path` = a folder of .uasset actors (e.g. .../__ExternalActors__/Level/<Level>)."""
    return run(path)


@mcp.tool()
def audit(path: str) -> dict:
    """Health summary of a level: device counts, duplicate actor names, warnings."""
    return audit_level(path)


@mcp.tool()
def find(path: str, query: str) -> list[str]:
    """Search a project (folder) for files whose package names anything matching `query`."""
    return search(build_index(path), query)


@mcp.tool()
def who_uses(path: str, target: str) -> list[str]:
    """Files in `path` that reference an asset matching `target` (where-used / impact)."""
    return impact(build_index(path), target) or where_used(build_index(path), target)


@mcp.tool()
def read_actor(file: str) -> dict:
    """Decode one placed-actor .uasset: {export_name: {property: value}} — includes
    Verse-VM device settings & values that live reflection cannot read."""
    pkg = read_package(file)
    out = {}
    for e in pkg.exports:
        props = decode_properties(pkg, e)
        if props:
            out[e.object_name] = props
    return out


@mcp.tool()
def editable_bindings(file: str) -> dict:
    """@editable device bindings of a placed Verse device (slot -> bound actor).
    Reads the wiring the editor GUI made — unreadable via live reflection."""
    return verse_bindings(read_package(file))


@mcp.tool()
def engine_devices(query: str) -> list[str]:
    """Search the offline Fortnite engine device catalog (1119 classes) by name."""
    return search_engine_devices(query)


if __name__ == "__main__":
    mcp.run()
