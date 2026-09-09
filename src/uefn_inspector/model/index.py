"""Project-wide index: parse every .uasset/.umap into one queryable model.

Generic — takes a directory, coupled to no specific project.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from uefn_inspector.core.uasset import Package, read_package


@dataclass
class ProjectIndex:
    root: str = ""
    packages: dict[str, Package] = field(default_factory=dict)  # path -> Package
    warnings: list[str] = field(default_factory=list)


def build_index(path: str | Path) -> ProjectIndex:
    root = Path(path)
    idx = ProjectIndex(root=str(root))
    for f in sorted([*root.rglob("*.uasset"), *root.rglob("*.umap")]):
        try:
            idx.packages[str(f)] = read_package(f)
        except Exception as exc:  # never let one file sink the index
            idx.warnings.append(f"{f.name}: {exc}")
    return idx
