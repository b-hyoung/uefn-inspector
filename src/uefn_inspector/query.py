"""Find/where-used queries over a ProjectIndex.

These answer the questions that were painful to do by hand in the editor:
"find X", "what uses X". Generic — no project assumptions.
"""
from __future__ import annotations

import re

from .graph import build_reference_graph
from .index import ProjectIndex
from .uasset import Package

_ENUM_TYPE = re.compile(r"^E[A-Z][A-Za-z0-9]+$")


def search(index: ProjectIndex, query: str) -> list[str]:
    """File paths whose package names any string matching `query` (case-insensitive)."""
    q = query.lower()
    hits = [
        path for path, pkg in index.packages.items()
        if any(q in name.lower() for name in pkg.names)
    ]
    return sorted(hits)


def where_used(index: ProjectIndex, target: str) -> list[str]:
    """File paths that reference a content object/asset matching `target`."""
    g = build_reference_graph(index)
    users: set[str] = set()
    for ref_target, sources in g.reverse.items():
        if target in ref_target:
            users |= sources
    return sorted(users)


def list_settings(pkg: Package) -> dict[str, list[str]]:
    """Surface a device's setting labels and enum types from the name table.

    Reports what settings *exist* (names), not their values — values of
    Verse-VM device settings are not readable offline (see capability matrix).
    """
    display = sorted(n for n in pkg.names if " " in n)
    enums = sorted(n for n in pkg.names if _ENUM_TYPE.match(n))
    return {"display_settings": display, "enums": enums}
