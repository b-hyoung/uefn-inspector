"""Reference graph over a ProjectIndex: who references what.

A reference target is any content object/package path a package names
(``/...`` excluding engine ``/Script`` code paths). Generic — no project
assumptions.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .index import ProjectIndex


def _references(names: list[str]) -> set[str]:
    return {n for n in names if n.startswith("/") and not n.startswith("/Script")}


@dataclass
class ReferenceGraph:
    forward: dict[str, set[str]] = field(default_factory=dict)   # file path -> targets
    reverse: dict[str, set[str]] = field(default_factory=dict)   # target -> file paths


def build_reference_graph(index: ProjectIndex) -> ReferenceGraph:
    g = ReferenceGraph()
    for path, pkg in index.packages.items():
        targets = _references(pkg.names)
        g.forward[path] = targets
        for t in targets:
            g.reverse.setdefault(t, set()).add(path)
    return g
