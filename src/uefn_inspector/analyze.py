"""Dependency / validation analyses over a ProjectIndex or a plain graph.

Algorithm functions take plain data (dicts/sets) so they are trivially
testable and reusable; project wrappers apply them to the reference graph.
"""
from __future__ import annotations

from .graph import build_reference_graph
from .index import ProjectIndex

DEFAULT_IGNORE = ("/Script", "/Engine")


def find_cycles(adjacency: dict[str, list[str]]) -> list[list[str]]:
    """Return simple cycles in a directed graph (DFS back-edge detection)."""
    cycles: list[list[str]] = []
    WHITE, GREY, BLACK = 0, 1, 2
    color: dict[str, int] = {n: WHITE for n in adjacency}
    stack: list[str] = []

    def visit(node: str) -> None:
        color[node] = GREY
        stack.append(node)
        for nxt in adjacency.get(node, []):
            if color.get(nxt, WHITE) == GREY:  # back-edge -> cycle
                cycles.append(stack[stack.index(nxt):] + [nxt])
            elif color.get(nxt, WHITE) == WHITE:
                visit(nxt)
        stack.pop()
        color[node] = BLACK

    for n in list(adjacency):
        if color[n] == WHITE:
            visit(n)
    return cycles


def impact(index: ProjectIndex, target: str) -> list[str]:
    """Files affected if `target` changes: everything that references it."""
    g = build_reference_graph(index)
    hit: set[str] = set()
    for ref_target, sources in g.reverse.items():
        if target in ref_target:
            hit |= sources
    return sorted(hit)


def find_orphans(nodes: set[str], edges: dict[str, set[str]]) -> list[str]:
    """Nodes that nothing references."""
    referenced: set[str] = set()
    for targets in edges.values():
        referenced |= targets
    return sorted(n for n in nodes if n not in referenced)


def find_broken_refs(known: set[str], references: set[str],
                     ignore_prefixes: tuple[str, ...] = DEFAULT_IGNORE) -> list[str]:
    """References that resolve to nothing known (excluding engine/script paths)."""
    broken = [
        r for r in references
        if r not in known and not r.startswith(ignore_prefixes)
    ]
    return sorted(broken)
