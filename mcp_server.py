"""MCP server for uefn-inspector — OFFLINE read/write of UEFN project files as
tools any Claude session can call. Complements the live uefn/unreal MCPs (which
need the editor open and cannot touch Verse-VM data): this one reads the files
directly, editor open or closed, and writes them with the editor closed.

The `instructions` string below is injected into every session's system prompt
by the MCP host — it is the leash that stops a session from concluding "GUI
only" after a live-MCP failure without checking `capabilities` first.

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
from uefn_inspector.level import audit_level, inspect_level as _inspect_level  # noqa: E402
from uefn_inspector.analysis.spatial import ascii_map, spatial_extent  # noqa: E402
from uefn_inspector.core.properties import decode_properties  # noqa: E402
from uefn_inspector.analysis.query import search, where_used  # noqa: E402
from uefn_inspector.core.uasset import read_package  # noqa: E402
from uefn_inspector.analysis.verse import verse_bindings  # noqa: E402
from uefn_inspector.capabilities import _editor_running  # noqa: E402
from uefn_inspector.edit.wire import actor_target, bind_editable as _bind_editable  # noqa: E402

INSTRUCTIONS = """\
uefn-inspector = OFFLINE UEFN project-file tool (reads/writes .uasset/.umap directly, editor closed).
It does what the live UEFN MCPs (unreal-mcp :8000, uefn listener :8765, unrealclaude) CANNOT:
read Verse-VM device settings, read AND write @editable device wiring (slot -> actor).

Rules for any UEFN request that changes a device value, setting, or @editable wiring:
1. Before saying "GUI only", "Details panel needed", "not possible" or "blocked": call `capabilities`
   and check its result. A live-MCP failure ("not valid ScriptDevice", type rejected, setting not
   saved) is NOT proof of impossibility — it is the signal that the job belongs to this server.
2. Order of tools: live MCP for placing actors, transforms, Verse BuildAll, PIE and editor logs;
   THIS server for Verse-VM values and @editable wiring (`read_actor`, `editable_bindings`,
   `bind_editable`). Writes need the editor closed; `bind_editable` refuses while it is open.
3. Report "GUI needed" only when `capabilities` / the offline table has no path either, and attach
   that result as evidence. Publish acceptance of size-changing writes is still unverified: work
   on a copy, keep the .bak.
"""

mcp = FastMCP("uefn-inspector", instructions=INSTRUCTIONS)


@mcp.tool()
def capabilities(sample_file: str = "") -> dict:
    """CALL THIS BEFORE saying a UEFN change is "GUI only", "not possible" or
    "blocked" — especially right after a live-MCP failure. Every entry is
    verified by RUNNING it now, not read from documentation: ok / blocked /
    unavailable / unverified with evidence. Pass a placed-actor .uasset as
    `sample_file` for a full check (bindings, property decode, size-changing
    edit); without it those report "unverified". Also reports preconditions:
    editor open (blocks offline writes), engine catalog present, live MCP reachable."""
    return _probe(sample_file or None)


@mcp.tool()
def inspect_level(path: str) -> dict:
    """OFFLINE (editor may be open or closed). Inventory of a UEFN level/actor
    directory from the files: device counts, asset refs, warnings. No editor
    load, no freeze — use instead of live `find_actors` scans. `path` = a folder
    of .uasset actors (e.g. .../__ExternalActors__/Level/<Level>)."""
    return run(path)


@mcp.tool()
def audit(path: str) -> dict:
    """OFFLINE health summary of a level from its files: device counts, duplicate
    actor names, leftover/orphan actors, warnings. Safe while the editor is open."""
    return audit_level(path)


@mcp.tool()
def level_map(path: str, cell: float = 500.0) -> dict:
    """OFFLINE. Top-down text map + zone table of a level directory, so the
    structure can be EXPLAINED, not just listed: which classes sit where
    (centroid, x/y range, count), overall extent, unplaced actors, and a
    `brief_template` for levels/LEVEL-X/build.md (theme / zones / flow /
    screenshots). Required by ticket 1 acceptance (structure brief). `cell` =
    map cell size in cm (500 = 5 m)."""
    lvl = _inspect_level(path)
    placed = [(a.device_class or "?", tuple(a.location)) for a in lvl.actors if a.location]
    out = ascii_map(placed, cell=cell)
    by_class: dict[str, list[tuple]] = {}
    for cls, loc in placed:
        by_class.setdefault(cls, []).append(loc)
    zones = []
    for cls, locs in sorted(by_class.items(), key=lambda kv: -len(kv[1])):
        n = len(locs)
        xs, ys, zs = [l[0] for l in locs], [l[1] for l in locs], [l[2] for l in locs]
        zones.append({"class": cls, "count": n,
                      "centroid": (sum(xs) / n, sum(ys) / n, sum(zs) / n),
                      "x_range": (min(xs), max(xs)), "y_range": (min(ys), max(ys))})
    return {
        "level": lvl.name, "actors": len(lvl.actors), "placed": len(placed),
        "unplaced": [f"{a.device_class} {a.name}".strip() for a in lvl.actors if not a.location],
        "extent": spatial_extent([loc for _, loc in placed]),
        "map": out["map"], "legend": out["legend"], "cell": out["cell"], "bounds": out["bounds"],
        "zones": zones,
        "brief_template": {
            "theme": "1 line: what this place is (backstage, flooded factory...) and its palette",
            "zones": "one row per zone: name / purpose (goal, danger, route, safe, boundary) / map symbol / assets used",
            "flow": "spawn -> first decision -> goal -> exit, in map coordinates; where the tension peaks",
            "screenshots": "3 viewport shots: spawn view, goal view, top-down; under levels/LEVEL-X/visual/",
        },
        "warnings": lvl.warnings,
    }


@mcp.tool()
def find(path: str, query: str) -> list[str]:
    """OFFLINE search of a project folder: files whose package references anything
    matching `query` (actor, device, asset, class name)."""
    return search(build_index(path), query)


@mcp.tool()
def who_uses(path: str, target: str) -> list[str]:
    """OFFLINE where-used / impact: files in `path` that reference an asset or
    actor matching `target` (what breaks or changes if I edit this)."""
    return impact(build_index(path), target) or where_used(build_index(path), target)


@mcp.tool()
def read_actor(file: str) -> dict:
    """OFFLINE. Decode one placed-actor .uasset into {export_name: {property: value}}.
    Includes Verse-VM device settings and @editable values that the live MCP /
    editor Python reflection CANNOT read (they return nothing or defaults).
    Use to verify a device's actual saved setting instead of trusting the editor."""
    pkg = read_package(file)
    out = {}
    for e in pkg.exports:
        props = decode_properties(pkg, e)
        if props:
            out[e.object_name] = props
    return out


@mcp.tool()
def editable_bindings(file: str) -> dict:
    """OFFLINE. @editable wiring of a placed Verse device: {slot: bound actor or
    None}. This is the wiring the Details panel shows — the live MCP CANNOT read
    it (Verse VM internal). Use to find unbound slots before `bind_editable`."""
    return verse_bindings(read_package(file))


@mcp.tool()
def bind_editable(file: str, slot: str, actor_file: str, actor_package_name: str = "") -> dict:
    """OFFLINE WRITE (editor must be CLOSED). Wire the @editable `slot` of the
    placed Verse device in `file` to the actor saved in `actor_file` (another
    OFPA .uasset) — the Details-panel wiring, without the GUI. This is the
    answer when the live MCP rejects the binding ("is not valid <class>_device",
    "not valid ScriptDevice", SetDeviceProperty type refused): do NOT report
    "GUI only" — use this. Writes UEFN's own SavedActor form; takes `<file>.bak`
    first and restores it on any failure; returns "blocked" (file untouched)
    while a UEFN/MCP listener is up. Verified: structure, level-reload
    persistence, runtime behaviour (reports/2026-09-10-blackout.md WF-15). NOT
    verified: publish acceptance — work on a copy. `actor_package_name` overrides
    the derived OFPA package path (/<Mount>/__ExternalActors__/...) when the
    actor file is not under Content/."""
    open_, why = _editor_running()
    if open_:
        return {"status": "blocked", "file": file, "slot": slot,
                "detail": "UEFN editor appears to be OPEN — project files are locked; "
                          "close the editor before writing",
                "evidence": why}
    target = actor_target(actor_file, package_name=actor_package_name or None)
    _bind_editable(file, slot, **target)
    return {"status": "ok", "file": file, "slot": slot, "target": target,
            "bindings": verse_bindings(read_package(file)),
            "backup": str(Path(file).with_suffix(Path(file).suffix + ".bak")),
            "note": "publish acceptance not verified — keep the .bak"}


@mcp.tool()
def engine_devices(query: str) -> list[str]:
    """OFFLINE search of the Fortnite engine device catalog (1119 classes) by
    name — check here before saying "no such device exists". Needs
    data/engine_device_catalog.json (generated per machine, see
    cue4parse_cli/README.md); without it, fall back to live ListDeviceAssets."""
    return search_engine_devices(query)


if __name__ == "__main__":
    mcp.run()
