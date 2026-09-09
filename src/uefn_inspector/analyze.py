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


def asset_usage(index: ProjectIndex, class_substrings: tuple[str, ...]) -> dict[str, list[str]]:
    """Map an imported asset (by class type) -> files that reference it.

    Component classes (``*Component``) are excluded: they are not assets.
    """
    usage: dict[str, set[str]] = {}
    for path, pkg in index.packages.items():
        for imp in pkg.imports:
            cls = imp.class_name
            if cls.endswith("Component"):
                continue
            if any(sub in cls for sub in class_substrings):
                usage.setdefault(imp.object_name, set()).add(path)
    return {k: sorted(v) for k, v in usage.items()}


def hotspots(index: ProjectIndex) -> list[tuple[str, int]]:
    """Most-referenced content targets (fan-in), descending."""
    g = build_reference_graph(index)
    ranked = [(t, len(srcs)) for t, srcs in g.reverse.items()]
    return sorted(ranked, key=lambda x: (-x[1], x[0]))


def fan_out(index: ProjectIndex) -> dict[str, int]:
    """How many content targets each file references."""
    g = build_reference_graph(index)
    return {path: len(targets) for path, targets in g.forward.items()}


def dependency_depth(adjacency: dict[str, list[str]]) -> int:
    """Longest chain length (in nodes) of a DAG. 0 if empty."""
    memo: dict[str, int] = {}

    def depth(node: str) -> int:
        if node in memo:
            return memo[node]
        memo[node] = 1  # guard against cycles
        best = 1 + max((depth(n) for n in adjacency.get(node, [])), default=0)
        memo[node] = best
        return best

    return max((depth(n) for n in adjacency), default=0)


def transitive_reachable(adjacency: dict[str, list[str]], start: str) -> set[str]:
    """All nodes reachable from `start` (excluding start itself)."""
    seen: set[str] = set()
    stack = list(adjacency.get(start, []))
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(adjacency.get(node, []))
    seen.discard(start)
    return seen


def to_dot(index: ProjectIndex) -> str:
    """Reference graph as Graphviz DOT."""
    g = build_reference_graph(index)
    lines = ["digraph refs {"]
    for path, targets in g.forward.items():
        src = path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1]
        for t in sorted(targets):
            leaf = t.rsplit("/", 1)[-1]
            lines.append(f'  "{src}" -> "{leaf}";')
    lines.append("}")
    return "\n".join(lines)


def to_mermaid(index: ProjectIndex) -> str:
    """Reference graph as a mermaid diagram (file name -> target leaf)."""
    g = build_reference_graph(index)
    lines = ["graph LR"]
    for path, targets in g.forward.items():
        src = path.rsplit("\\", 1)[-1].rsplit("/", 1)[-1]
        for t in sorted(targets):
            leaf = t.rsplit("/", 1)[-1]
            lines.append(f'  "{src}" --> "{leaf}"')
    return "\n".join(lines)


def mesh_usage(index: ProjectIndex) -> dict[str, list[str]]:
    return asset_usage(index, ("StaticMesh", "SkeletalMesh"))


def material_usage(index: ProjectIndex) -> dict[str, list[str]]:
    return asset_usage(index, ("Material",))


def curve_usage(index: ProjectIndex) -> dict[str, list[str]]:
    return asset_usage(index, ("Curve",))
