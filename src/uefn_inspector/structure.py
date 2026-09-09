"""Object-structure analyses within a package: components, containment, refs.

Generic — no project assumptions.
"""
from __future__ import annotations

from .index import ProjectIndex
from .uasset import Package


def _resolve_class(pkg: Package, class_index: int) -> str:
    """Resolve an export's class FPackageIndex to a class name.

    The import pointed at *is* the class: its object_name is the class name
    (e.g. "AudioComponent"), while its class_name is the meta ("Class").
    """
    if class_index < 0:
        imp_idx = -class_index - 1
        if 0 <= imp_idx < len(pkg.imports):
            return pkg.imports[imp_idx].object_name
    return ""


def component_composition(pkg: Package) -> list[str]:
    """Component class names contained in this package (actor -> its components)."""
    comps = []
    for e in pkg.exports:
        cls = _resolve_class(pkg, e.class_index)
        if cls.endswith("Component"):
            comps.append(cls)
    return comps


def outer_tree(pkg: Package) -> dict[str, str]:
    """child object name -> parent object name (via export OuterIndex)."""
    tree: dict[str, str] = {}
    for e in pkg.exports:
        if e.outer_index > 0:  # positive FPackageIndex -> export
            parent_i = e.outer_index - 1
            if 0 <= parent_i < len(pkg.exports):
                tree[e.object_name] = pkg.exports[parent_i].object_name
    return tree


def soft_hard_refs(pkg: Package) -> dict[str, list[str]]:
    """Split references into hard (import table) and soft (name-only paths)."""
    hard = {
        r for imp in pkg.imports
        for r in (imp.class_package, imp.object_name)
        if r.startswith("/") and not r.startswith("/Script")
    }
    all_paths = {n for n in pkg.names if n.startswith("/") and not n.startswith("/Script")}
    soft = all_paths - hard
    return {"hard": sorted(hard), "soft": sorted(soft)}


def arch_lint(index: ProjectIndex, max_components: int = 12) -> list[str]:
    """Files whose actor holds more than `max_components` components."""
    return sorted(
        path for path, pkg in index.packages.items()
        if len(component_composition(pkg)) > max_components
    )
